import { vi } from 'vitest';
import { SearchService } from '../searchService';
import { PerplexitySearchResult } from '../../types/sourceTrace';

// Mock environment variables
vi.mock('import.meta.env', () => ({
  env: {
    VITE_PERPLEXITY_API_KEY: undefined // Test the mock data path
  }
}));

describe('SearchService', () => {
  let searchService: SearchService;

  beforeEach(() => {
    searchService = new SearchService();
  });

  describe('search', () => {
    it('should throw an error when no search input is provided', async () => {
      await expect(searchService.search({})).rejects.toThrow(
        'At least one of text, image_urls, or urls must be provided'
      );
    });

    it('should return mock results when API key is not available', async () => {
      const result = await searchService.search({ text: 'test query' });
      
      expect(result.originalSources).toHaveLength(3);
      expect(result.viralPoints).toHaveLength(3);
      
      // Verify mock data structure
      result.originalSources.forEach((source) => {
        expect(source.title).toContain('Mock Result');
        expect(source.url).toContain('example.com');
        expect(source.snippet).toContain('test query');
        expect(source.platform).toBeDefined();
        expect(source.engagement_metrics).toBeDefined();
      });
    });

    it('should sort results by timestamp for original sources', async () => {
      const result = await searchService.search({ text: 'test query' });
      
      // Verify that original sources are sorted by timestamp
      const timestamps = result.originalSources.map(source => new Date(source.timestamp).getTime());
      const isSorted = timestamps.every((time, index) => 
        index === 0 || time >= timestamps[index - 1]
      );
      
      expect(isSorted).toBe(true);
    });

    it('should sort viral points by engagement metrics', async () => {
      const result = await searchService.search({ text: 'test query' });
      
      // Verify that viral points are sorted by engagement
      const engagementScores = result.viralPoints.map(point => 
        (point.engagement_metrics?.views || 0) +
        (point.engagement_metrics?.shares || 0) +
        (point.engagement_metrics?.comments || 0)
      );
      
      const isSorted = engagementScores.every((score, index) => 
        index === 0 || score <= engagementScores[index - 1]
      );
      
      expect(isSorted).toBe(true);
    });
  });
}); 