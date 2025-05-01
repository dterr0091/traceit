import { SearchInput, SearchResult, ViralMoment } from '../types';
import { AIAnalysisService } from './aiAnalysis';
import { PlatformRegistry } from '../platforms/registry';

export class SearchService {
  private aiAnalysisService: AIAnalysisService;
  private platformRegistry: PlatformRegistry;
  private searchCache: Map<string, SearchResult>;
  private rateLimits: Map<string, number>;

  constructor() {
    this.aiAnalysisService = new AIAnalysisService();
    this.platformRegistry = new PlatformRegistry();
    this.searchCache = new Map();
    this.rateLimits = new Map();
  }

  /**
   * Executes a search across multiple platforms
   * @param input The search input
   * @param userId Optional user ID for rate limiting
   * @returns Promise containing the search results
   */
  async search(input: SearchInput, userId?: string): Promise<SearchResult> {
    if (userId && !this.checkRateLimit(userId)) {
      throw new Error('Rate limit exceeded');
    }

    const cacheKey = this.generateCacheKey(input);
    const cachedResult = this.searchCache.get(cacheKey);
    if (cachedResult) {
      return cachedResult;
    }

    const analysis = await this.aiAnalysisService.analyze(input);
    const platformResults = await this.platformRegistry.searchAcrossPlatforms(input, analysis);
    const results = this.combineResults(platformResults);
    
    this.searchCache.set(cacheKey, results);
    if (userId) {
      this.incrementRateLimit(userId);
    }

    return results;
  }

  private combineResults(platformResults: SearchResult[]): SearchResult {
    if (platformResults.length === 0) {
      return {
        viralMoments: [],
        confidenceScore: 0,
        suggestedSearches: ['No results found'],
        alternativeQueries: ['Try different search terms']
      };
    }

    // Find the most likely original source across all platforms
    const originalSources = platformResults
      .map(result => result.originalSource)
      .filter((source): source is NonNullable<typeof source> => source !== undefined)
      .sort((a, b) => b.confidenceScore - a.confidenceScore);

    // Combine all viral moments
    const allViralMoments = platformResults
      .flatMap(result => result.viralMoments)
      .sort((a, b) => {
        const aMetrics = a.metrics || {};
        const bMetrics = b.metrics || {};
        return (
          (bMetrics.views || 0) - (aMetrics.views || 0) ||
          (bMetrics.shares || 0) - (aMetrics.shares || 0) ||
          (bMetrics.likes || 0) - (aMetrics.likes || 0)
        );
      });

    // Calculate overall confidence score
    const avgConfidence = platformResults.reduce(
      (sum, result) => sum + result.confidenceScore,
      0
    ) / platformResults.length;

    return {
      originalSource: originalSources[0],
      viralMoments: allViralMoments,
      confidenceScore: avgConfidence
    };
  }

  private generateCacheKey(input: SearchInput): string {
    return `${input.type}:${input.content}`;
  }

  private checkRateLimit(userId: string): boolean {
    const currentTime = Date.now();
    const userLimit = this.rateLimits.get(userId) || 0;
    
    // Reset rate limit if more than 1 hour has passed
    if (currentTime - userLimit > 3600000) {
      this.rateLimits.set(userId, currentTime);
      return true;
    }
    
    // Check if user has made more than 100 requests in the last hour
    return this.rateLimits.get(userId) === currentTime;
  }

  private incrementRateLimit(userId: string): void {
    const currentTime = Date.now();
    this.rateLimits.set(userId, currentTime);
  }
} 