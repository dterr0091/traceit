import { SearchResult, SearchState, PerplexitySearchResult } from '../types/sourceTrace';
import { mockSearchResults, generateExtendedGraphData, simulateApiDelay } from './mockData';

export class SearchService {
  private apiKey: string;

  constructor() {
    // We no longer need to validate API key since we're using mock data
    this.apiKey = import.meta.env.VITE_PERPLEXITY_API_KEY || 'mock-key';
    console.log('SearchService initialized with mock data support');
  }

  async search(query: string): Promise<SearchResult[]> {
    try {
      console.log('Using mock data for search query:', query);
      
      // Simulate API delay
      await simulateApiDelay(2000);
      
      // Return mock data
      const mockResults = [...mockSearchResults];
      
      // Customize the first result to reference the search query
      if (mockResults.length > 0 && mockResults[0].isOriginalSource) {
        mockResults[0].title = `Original Source: ${query}`;
      }
      
      // Generate additional results if needed
      const enrichedResults = generateExtendedGraphData(mockResults);
      
      return enrichedResults;
    } catch (error) {
      console.error('Search error (using mock fallback):', error);
      return mockSearchResults; // Always return mock data even on error
    }
  }

  // Keeping this method for reference but not using it
  private transformSearchResults(data: any, originalQuery: string): SearchResult[] {
    // This method is no longer used since we're returning mock data directly
    console.log('Using mock data instead of transforming API results');
    return mockSearchResults;
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