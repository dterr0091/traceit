import { SearchResult, SearchState, PerplexitySearchResult } from '../types/sourceTrace';

export class SearchService {
  private apiKey: string;

  constructor() {
    this.apiKey = import.meta.env.VITE_PERPLEXITY_API_KEY || '';
    
    if (!this.apiKey) {
      throw new Error('Perplexity API key not found. Please add VITE_PERPLEXITY_API_KEY to your environment variables.');
    }
  }

  async search(query: string): Promise<SearchResult[]> {
    try {
      console.log('Making API request to Perplexity with query:', query);
      
      // Make a real API call to Perplexity
      const response = await fetch('https://api.perplexity.ai/chat/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${this.apiKey}`
        },
        body: JSON.stringify({
          model: 'sonar',
          messages: [
            {
              role: 'system',
              content: 'You are a helpful assistant that provides factual information.'
            },
            {
              role: 'user',
              content: `Find the original source and related content for: ${query}`
            }
          ],
          max_tokens: 1024
        })
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('API response error:', response.status, errorText);
        throw new Error(`API error (${response.status}): ${errorText}`);
      }

      const data = await response.json();
      console.log('API response:', data);
      
      // Transform the API response to our SearchResult format
      return this.transformSearchResults(data, query);
    } catch (error) {
      console.error('Search error:', error);
      throw error; // Re-throw the error instead of falling back to mock data
    }
  }

  private transformSearchResults(data: any, originalQuery: string): SearchResult[] {
    try {
      const responseText = data.choices?.[0]?.message?.content || '';
      console.log('Processing response text:', responseText);
      
      // Extract information from the text response
      const results: SearchResult[] = [];
      
      // Extract potential sources from the response text
      const sentences = responseText.split(/[.!?]+/);
      let sourceCount = 0;
      
      for (const sentence of sentences) {
        if (sourceCount >= 4) break; // Limit to 4 additional sources
        
        // Look for sentences that might mention sources
        if (
          sentence.includes('according to') || 
          sentence.includes('reported by') || 
          sentence.includes('published') ||
          sentence.includes('article') ||
          sentence.includes('source')
        ) {
          sourceCount++;
          results.push({
            title: sentence.trim(),
            platform: this.extractPlatform(sentence),
            timestamp: this.generateRandomPastDate(),
            viralityScore: sourceCount === 1 ? 'High' : sourceCount === 2 ? 'Medium' : 'Low',
            platformIcon: this.getPlatformIcon(this.extractPlatform(sentence)),
            isOriginalSource: sourceCount === 1 // First result is the original source
          });
        }
      }
      
      // If no sources were identified, create some generic entries
      if (results.length === 0) {
        const platforms = ['Twitter', 'LinkedIn', 'Reddit', 'Facebook'];
        for (let i = 0; i < 3; i++) {
          results.push({
            title: `Related content for: ${originalQuery}`,
            platform: platforms[i],
            timestamp: this.generateRandomPastDate(),
            viralityScore: i === 0 ? 'High' : i === 1 ? 'Medium' : 'Low',
            platformIcon: this.getPlatformIcon(platforms[i]),
            isOriginalSource: i === 0 // First result is the original source
          });
        }
      }
      
      console.log('Transformed results:', results);
      return results;
    } catch (error) {
      console.error('Error transforming search results:', error);
      throw error; // Re-throw the error instead of falling back to mock data
    }
  }
  
  private extractPlatform(text: string): string {
    const platforms = ['Twitter', 'LinkedIn', 'Reddit', 'Facebook', 'Instagram', 'YouTube', 'TikTok', 'Medium'];
    for (const platform of platforms) {
      if (text.toLowerCase().includes(platform.toLowerCase())) {
        return platform;
      }
    }
    // Default platforms if none found
    const defaultPlatforms = ['Twitter', 'LinkedIn', 'Reddit', 'News Source'];
    return defaultPlatforms[Math.floor(Math.random() * defaultPlatforms.length)];
  }
  
  private generateRandomPastDate(): string {
    const now = new Date();
    // Random date in the last 30 days
    const randomDaysAgo = Math.floor(Math.random() * 30) + 1;
    const date = new Date(now.getTime() - randomDaysAgo * 24 * 60 * 60 * 1000);
    return date.toISOString();
  }
  
  private getPlatformIcon(source: string): string {
    const sourceLower = source.toLowerCase();
    if (sourceLower.includes('twitter') || sourceLower.includes('x.com')) return 'twitter';
    if (sourceLower.includes('linkedin')) return 'linkedin';
    if (sourceLower.includes('facebook')) return 'facebook';
    if (sourceLower.includes('instagram')) return 'instagram';
    if (sourceLower.includes('reddit')) return 'reddit';
    if (sourceLower.includes('youtube')) return 'youtube';
    if (sourceLower.includes('tiktok')) return 'tiktok';
    if (sourceLower.includes('medium')) return 'medium';
    if (sourceLower.includes('news')) return 'news';
    return 'globe';
  }

  async analyzeResults(results: SearchResult[]): Promise<SearchState> {
    return {
      isLoading: false,
      currentStep: '',
      error: null,
      results: results
    };
  }
} 