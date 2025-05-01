import { SearchInput, SearchResult, ContentAnalysis } from './types';
import { AIAnalysisService } from './services/aiAnalysis';
import { SearchService } from './services/searchService';

export class SearchEngine {
  private aiAnalysisService: AIAnalysisService;
  private searchService: SearchService;

  constructor() {
    this.aiAnalysisService = new AIAnalysisService();
    this.searchService = new SearchService();
  }

  /**
   * Analyzes the input content to identify key elements and characteristics
   * @param input The search input to analyze
   * @returns Promise containing the content analysis results
   */
  async analyzeContent(input: SearchInput): Promise<ContentAnalysis> {
    return this.aiAnalysisService.analyze(input);
  }

  /**
   * Executes the search based on analyzed content
   * @param input The search input to process
   * @param userId Optional user ID for rate limiting
   * @returns Promise containing the search results
   */
  async executeSearch(input: SearchInput, userId?: string): Promise<SearchResult> {
    try {
      return await this.searchService.search(input, userId);
    } catch (error) {
      if (error instanceof Error && error.message === 'Rate limit exceeded') {
        return {
          viralMoments: [],
          confidenceScore: 0,
          suggestedSearches: ['Please try again later'],
          alternativeQueries: ['Your search has been rate limited']
        };
      }
      
      // For other errors, return a generic error response
      return {
        viralMoments: [],
        confidenceScore: 0,
        suggestedSearches: ['Try a different search'],
        alternativeQueries: ['Search with different keywords']
      };
    }
  }
} 