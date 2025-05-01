import { z } from 'zod';
import OpenAI from 'openai';
import { config } from '@/config';

// Type definitions for content analysis
export type ContentType = 'text' | 'url' | 'image' | 'video';

export interface ContentAnalysisResult {
  type: ContentType;
  keyElements: string[];
  characteristics: Record<string, string>;
  confidence: number;
  timestamp: string;
}

export interface MediaAnalysisResult extends ContentAnalysisResult {
  features: string[];
  patterns: string[];
}

export interface TextAnalysisResult extends ContentAnalysisResult {
  semanticMeaning: string;
  entities: string[];
  topics: string[];
}

// Input validation schema
export const contentInputSchema = z.object({
  content: z.string(),
  type: z.enum(['text', 'url', 'image', 'video']),
  metadata: z.record(z.unknown()).optional(),
});

export class ContentAnalysisService {
  private static instance: ContentAnalysisService;
  private openai: OpenAI;

  private constructor() {
    this.openai = new OpenAI({
      apiKey: config.OPENAI_API_KEY,
    });
  }

  public static getInstance(): ContentAnalysisService {
    if (!ContentAnalysisService.instance) {
      ContentAnalysisService.instance = new ContentAnalysisService();
    }
    return ContentAnalysisService.instance;
  }

  /**
   * Analyzes the input content and returns structured analysis results
   * @param input The content to analyze
   * @returns Promise<ContentAnalysisResult>
   */
  public async analyzeContent(input: z.infer<typeof contentInputSchema>): Promise<ContentAnalysisResult> {
    try {
      // Validate input
      const validatedInput = contentInputSchema.parse(input);

      // Route to appropriate analysis method based on content type
      switch (validatedInput.type) {
        case 'image':
        case 'video':
          return this.analyzeMedia(validatedInput);
        case 'text':
        case 'url':
          return this.analyzeText(validatedInput);
        default:
          throw new Error(`Unsupported content type: ${validatedInput.type}`);
      }
    } catch (error) {
      console.error('Content analysis failed:', error);
      throw error;
    }
  }

  /**
   * Analyzes media content (images/videos) to extract features and patterns
   * @param input The media content to analyze
   * @returns Promise<MediaAnalysisResult>
   */
  private async analyzeMedia(input: z.infer<typeof contentInputSchema>): Promise<MediaAnalysisResult> {
    try {
      // Use OpenAI's vision API for image analysis
      const response = await this.openai.chat.completions.create({
        model: "gpt-4-vision-preview",
        messages: [
          {
            role: "system",
            content: `You are TraceAI: a world-class discovery engine whose sole mission is to locate and describe the ORIGINAL and MOST VIRAL instances of any online content. When given a user query—whether a URL, text snippet, image, or video—you must:

1. **Decompose the query** into its meaningful parts (e.g. video visuals, audio track, overlaid text, hashtags, captions, metadata).
2. **Analyze each component** separately:
   - For video: identify visual trends, repeated motifs, key frames.
   - For audio: detect recurring sounds, music clips, voice samples, and their spread.
   - For text/metadata: extract phrases, hashtags, and their semantic clusters.
3. **Trace the lifecycle** of each component:
   - Find the **earliest known source** (creator handle, platform, timestamp).
   - Find the **peak viral moments** (highest share/view spikes, remix forks).
4. **Aggregate your findings** into a structured response:
   - **original_source:** { url, platform, creator, timestamp }
   - **viral_moments:** [{ platform, creator, timestamp, engagement_metrics }]
   - **breakdown:** { video_trends: [...], audio_trends: [...], text_trends: [...] }
5. **Describe** what you see and where it first appeared—never comment on whether it's "true" or "fake," only on content, creators, and chronology.

Always be concise, fact-driven, and structured. Your output is the single source of truth for "when and where did this content originate, and how did it go viral?"`
          },
          {
            role: "user",
            content: [
              { type: "text", text: "Analyze this image and provide its origin and viral spread information." },
              { 
                type: "image_url",
                image_url: {
                  url: input.content
                }
              }
            ]
          }
        ],
        max_tokens: 300
      });

      const analysis = response.choices[0].message?.content;
      if (!analysis) {
        throw new Error('Failed to analyze media content');
      }

      // Parse the analysis results
      const parsedAnalysis = this.parseMediaAnalysis(analysis);

      return {
        type: input.type,
        keyElements: parsedAnalysis.keyElements,
        characteristics: parsedAnalysis.characteristics,
        confidence: parsedAnalysis.confidence,
        timestamp: new Date().toISOString(),
        features: parsedAnalysis.features,
        patterns: parsedAnalysis.patterns,
      };
    } catch (error) {
      console.error('Media analysis failed:', error);
      throw error;
    }
  }

  /**
   * Analyzes text content or URLs to extract semantic meaning
   * @param input The text/URL content to analyze
   * @returns Promise<TextAnalysisResult>
   */
  private async analyzeText(input: z.infer<typeof contentInputSchema>): Promise<TextAnalysisResult> {
    try {
      // Use OpenAI's text analysis capabilities
      const response = await this.openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content: `You are TraceAI: a world-class discovery engine whose sole mission is to locate and describe the ORIGINAL and MOST VIRAL instances of any online content. When given a user query—whether a URL, text snippet, image, or video—you must:

1. **Decompose the query** into its meaningful parts (e.g. video visuals, audio track, overlaid text, hashtags, captions, metadata).
2. **Analyze each component** separately:
   - For video: identify visual trends, repeated motifs, key frames.
   - For audio: detect recurring sounds, music clips, voice samples, and their spread.
   - For text/metadata: extract phrases, hashtags, and their semantic clusters.
3. **Trace the lifecycle** of each component:
   - Find the **earliest known source** (creator handle, platform, timestamp).
   - Find the **peak viral moments** (highest share/view spikes, remix forks).
4. **Aggregate your findings** into a structured response:
   - **original_source:** { url, platform, creator, timestamp }
   - **viral_moments:** [{ platform, creator, timestamp, engagement_metrics }]
   - **breakdown:** { video_trends: [...], audio_trends: [...], text_trends: [...] }
5. **Describe** what you see and where it first appeared—never comment on whether it's "true" or "fake," only on content, creators, and chronology.

Always be concise, fact-driven, and structured. Your output is the single source of truth for "when and where did this content originate, and how did it go viral?"`
          },
          {
            role: "user",
            content: input.content
          }
        ],
        max_tokens: 300
      });

      const analysis = response.choices[0].message?.content;
      if (!analysis) {
        throw new Error('Failed to analyze text content');
      }

      // Parse the analysis results
      const parsedAnalysis = this.parseTextAnalysis(analysis);

      return {
        type: input.type,
        keyElements: parsedAnalysis.keyElements,
        characteristics: parsedAnalysis.characteristics,
        confidence: parsedAnalysis.confidence,
        timestamp: new Date().toISOString(),
        semanticMeaning: parsedAnalysis.semanticMeaning,
        entities: parsedAnalysis.entities,
        topics: parsedAnalysis.topics,
      };
    } catch (error) {
      console.error('Text analysis failed:', error);
      throw error;
    }
  }

  private parseMediaAnalysis(analysis: string): Omit<MediaAnalysisResult, 'type' | 'timestamp'> {
    // TODO: Implement proper parsing of media analysis results
    // This is a placeholder implementation
    return {
      keyElements: ['visual elements', 'composition', 'color scheme'],
      characteristics: {
        format: 'placeholder',
        resolution: 'placeholder',
      },
      confidence: 0.95,
      features: ['feature1', 'feature2'],
      patterns: ['pattern1', 'pattern2'],
    };
  }

  private parseTextAnalysis(analysis: string): Omit<TextAnalysisResult, 'type' | 'timestamp'> {
    // TODO: Implement proper parsing of text analysis results
    // This is a placeholder implementation
    return {
      keyElements: ['main topic', 'key phrases', 'sentiment'],
      characteristics: {
        language: 'placeholder',
        length: 'placeholder',
      },
      confidence: 0.95,
      semanticMeaning: 'placeholder semantic meaning',
      entities: ['entity1', 'entity2'],
      topics: ['topic1', 'topic2'],
    };
  }
} 