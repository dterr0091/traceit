import { v4 as uuidv4 } from 'uuid';
import OpenAI from 'openai';
import { ExtractedPost, AnalysisResult } from '../types/index';
import { PerplexityService } from './perplexity';
import { RedisService } from './redisService';
import { Thought, PrimaryThought, ThoughtLineage, QuotaStatus } from '../types/thoughts';
import { PerplexitySearchResult, SearchInput } from '../types/sourceTrace';

// Quota limits per user
const DAILY_QUOTA = 10;
// Expose quotaStore for testing
export const quotaStore: Record<string, QuotaStatus> = {};

export class SearchService {
  private openai: OpenAI;
  private perplexity: PerplexityService;
  private redis: RedisService;

  constructor() {
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });
    this.perplexity = new PerplexityService();
    this.redis = new RedisService();
  }

  // STAGE 0: Check user quota
  private async quotaGuard(userId: string): Promise<boolean> {
    if (!quotaStore[userId]) {
      // Initialize quota for new users
      quotaStore[userId] = {
        remaining: DAILY_QUOTA,
        limit: DAILY_QUOTA,
        reset: new Date(new Date().setHours(24, 0, 0, 0)) // Next midnight
      };
    }

    const quota = quotaStore[userId];
    
    // Check if quota has reset
    const now = new Date();
    if (now >= quota.reset) {
      quota.remaining = DAILY_QUOTA;
      quota.reset = new Date(new Date().setHours(24, 0, 0, 0)); // Next midnight
    }

    // Check if quota exhausted
    if (quota.remaining <= 0) {
      return false;
    }

    // Decrement quota
    quota.remaining--;
    return true;
  }

  // STAGE 1: Ingest and unify content
  private async ingestAndUnify(payload: ExtractedPost): Promise<string> {
    // Combine all relevant content into a unified blob
    const textContent = [
      payload.title || "",
      payload.content || payload.plainText || ""
    ].filter(Boolean).join("\n\n");

    // Add media descriptions if available
    let mediaDescriptions = "";
    if (payload.mediaUrls && payload.mediaUrls.length > 0) {
      mediaDescriptions = `Media URLs: ${payload.mediaUrls.join(", ")}`;
    }

    return `${textContent}\n\n${mediaDescriptions}`.trim();
  }

  // STAGE 2: Extract thoughts from content
  private async extractThoughts(contentBlob: string): Promise<Thought[]> {
    try {
      const response = await this.openai.chat.completions.create({
        model: "gpt-4-turbo",
        messages: [
          {
            role: "system",
            content: "You are an AI that extracts key thoughts or claims from content. Identify the most important assertions, claims, or ideas in the text. Return exactly 5 distinct thoughts."
          },
          {
            role: "user",
            content: contentBlob
          }
        ],
        temperature: 0.7,
        max_tokens: 1000
      });

      const content = response.choices[0]?.message?.content;
      if (!content) {
        throw new Error('Empty response from OpenAI');
      }

      // Parse the thoughts and create embeddings for each
      const thoughtTexts = content.split("\n")
        .filter(line => line.trim())
        .slice(0, 5); // Hard cap at 5 thoughts

      const thoughts: Thought[] = [];
      
      for (const thoughtText of thoughtTexts) {
        const cleanedText = thoughtText.replace(/^\d+[\.\)\-]\s*/, "").trim();
        
        // Generate embedding for the thought
        const embedding = await this.createEmbedding(cleanedText);
        
        thoughts.push({
          id: uuidv4(),
          content: cleanedText,
          embedding
        });
      }

      return thoughts;
    } catch (error) {
      console.error('Error extracting thoughts:', error);
      throw new Error('Failed to extract thoughts from content');
    }
  }

  // Helper method to create embeddings
  private async createEmbedding(text: string): Promise<number[]> {
    try {
      const response = await this.openai.embeddings.create({
        model: "text-embedding-3-small",
        input: text,
        encoding_format: "float"
      });

      return response.data[0].embedding;
    } catch (error) {
      console.error('Error creating embedding:', error);
      throw new Error('Failed to create embedding');
    }
  }

  // STAGE 3: Rank thoughts
  private async rankThoughts(thoughts: Thought[]): Promise<{ primary: Thought, secondary: Thought[] }> {
    try {
      // For now, use a simple approach: score thoughts based on specificity and importance
      const response = await this.openai.chat.completions.create({
        model: "gpt-4-turbo",
        messages: [
          {
            role: "system",
            content: "You are an AI that ranks thoughts based on how specific, verifiable, and important they are. Assign scores from 0-100 for each thought."
          },
          {
            role: "user",
            content: "Rank these thoughts by how specific, verifiable, and important they are. Return a JSON array with scores for each thought:\n\n" + 
              thoughts.map((t, i) => `${i+1}. ${t.content}`).join("\n\n")
          }
        ],
        temperature: 0.3,
        max_tokens: 500,
        response_format: { type: "json_object" }
      });

      const content = response.choices[0]?.message?.content;
      if (!content) {
        throw new Error('Empty response from OpenAI');
      }

      try {
        const scores = JSON.parse(content);
        
        // Apply scores to thoughts
        for (let i = 0; i < thoughts.length; i++) {
          thoughts[i].score = scores.scores[i] || scores[`thought${i+1}`] || scores[i];
        }
        
        // Sort thoughts by score in descending order
        const sortedThoughts = [...thoughts].sort((a, b) => 
          (b.score || 0) - (a.score || 0)
        );
        
        // Select primary thought and secondary thoughts
        const primary = sortedThoughts[0];
        const secondary = sortedThoughts.slice(1);
        
        return { primary, secondary };
      } catch (error) {
        console.error('Error parsing thought scores:', error);
        // Fallback: use the first thought as primary
        return { 
          primary: thoughts[0], 
          secondary: thoughts.slice(1) 
        };
      }
    } catch (error) {
      console.error('Error ranking thoughts:', error);
      // Fallback: use the first thought as primary
      return { 
        primary: thoughts[0], 
        secondary: thoughts.slice(1) 
      };
    }
  }

  // STAGE 4: Trace primary thought
  private async traceThought(thought: Thought): Promise<PrimaryThought> {
    try {
      // Search for evidence of the thought using Perplexity
      const searchResults = await this.perplexity.search(thought.content);
      
      // Determine if the thought is viral and its origin
      const response = await this.openai.chat.completions.create({
        model: "gpt-4-turbo",
        messages: [
          {
            role: "system",
            content: "You analyze search results for a claim to determine its origin and viral status. Return a JSON object with 'origin' (source name/author) and 'viral' (boolean)."
          },
          {
            role: "user",
            content: `Thought: ${thought.content}\n\nSearch Results: ${JSON.stringify(searchResults)}`
          }
        ],
        temperature: 0.3,
        max_tokens: 500,
        response_format: { type: "json_object" }
      });

      const content = response.choices[0]?.message?.content;
      if (!content) {
        throw new Error('Empty response from OpenAI');
      }

      const analysis = JSON.parse(content);
      
      // Create PrimaryThought with lineage info
      const primaryThought: PrimaryThought = {
        ...thought,
        origin: analysis.origin || "Unknown",
        viral: analysis.viral || false,
        evidence: searchResults
      };

      return primaryThought;
    } catch (error) {
      console.error('Error tracing thought:', error);
      
      // Return a basic primary thought with minimal info if tracing fails
      return {
        ...thought,
        origin: "Unknown",
        viral: false,
        evidence: []
      };
    }
  }

  // STAGE 5: Persist data
  private async persist(primary: PrimaryThought, secondary: Thought[]): Promise<void> {
    try {
      // Store primary thought
      await this.redis.storeThought(primary.id, primary);
      
      // Store secondary thoughts
      await this.redis.storeSecondaryThoughts(primary.id, secondary);
    } catch (error) {
      console.error('Error persisting thoughts:', error);
      throw new Error('Failed to persist thoughts');
    }
  }

  // Legacy search interface for backward compatibility
  public async search(inputOrUserId: string | SearchInput, post?: ExtractedPost): Promise<ThoughtLineage | PerplexitySearchResult[]> {
    // If called with the old interface, delegate to the legacy search method
    if (typeof inputOrUserId !== 'string') {
      return this.legacySearch(inputOrUserId);
    }
    
    // New search flow
    if (!post) {
      throw new Error('Post is required for the new search flow');
    }
    
    return this.traceSearch(inputOrUserId, post);
  }
  
  // Legacy search implementation for backward compatibility
  private async legacySearch(input: SearchInput): Promise<PerplexitySearchResult[]> {
    const { text, image_urls, urls, max_results = 4 } = input;

    if (!text && (!image_urls || image_urls.length === 0) && (!urls || urls.length === 0)) {
      throw new Error('At least one of text, image_urls, or urls must be provided');
    }

    // For now, we'll focus on text search. Image and URL search will be implemented later
    if (text) {
      return this.perplexity.search(text, max_results);
    }

    // Fallback error
    throw new Error('Image and URL search not yet implemented');
  }
  
  // New trace search implementation
  public async traceSearch(userId: string, post: ExtractedPost): Promise<ThoughtLineage> {
    // STAGE 0: Check quota
    const hasQuota = await this.quotaGuard(userId);
    if (!hasQuota) {
      throw new Error('Daily search quota exceeded');
    }
    
    // STAGE 1: Ingest and unify
    const contentBlob = await this.ingestAndUnify(post);
    
    // STAGE 2: Extract thoughts
    const thoughts = await this.extractThoughts(contentBlob);
    
    // STAGE 3: Rank thoughts
    const { primary, secondary } = await this.rankThoughts(thoughts);
    
    // STAGE 4: Trace primary thought
    const primaryWithLineage = await this.traceThought(primary);
    
    // STAGE 5: Persist
    await this.persist(primaryWithLineage, secondary);
    
    // Return lineage + secondary count
    return {
      primaryThought: primaryWithLineage,
      secondaryCount: secondary.length
    };
  }

  // Method to get secondary thoughts for a primary thought
  public async getSecondaryThoughts(primaryId: string): Promise<Thought[]> {
    return this.redis.getSecondaryThoughts(primaryId);
  }
  
  // Legacy analyze and search method for backward compatibility
  public async analyzeAndSearch(post: ExtractedPost): Promise<PerplexitySearchResult[]> {
    // Simply transform this into a trace search and return the evidence
    const userId = 'legacy-user'; // Use a default user ID for legacy calls
    const result = await this.traceSearch(userId, post);
    return result.primaryThought.evidence;
  }
} 