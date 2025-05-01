import { SearchEngine } from '../search';
import { SearchResult, SearchInput } from '../types';

describe('SearchEngine', () => {
  let searchEngine: SearchEngine;

  beforeEach(() => {
    searchEngine = new SearchEngine();
  });

  describe('analyzeContent', () => {
    it('should analyze URL input correctly', async () => {
      const input: SearchInput = {
        type: 'url',
        content: 'https://twitter.com/user/status/1234567890'
      };

      const analysis = await searchEngine.analyzeContent(input);
      expect(analysis).toHaveProperty('keyElements');
      expect(analysis).toHaveProperty('characteristics');
      expect(analysis).toHaveProperty('confidenceScore');
    });

    it('should analyze text input correctly', async () => {
      const input: SearchInput = {
        type: 'text',
        content: 'Find the original source of this viral tweet'
      };

      const analysis = await searchEngine.analyzeContent(input);
      expect(analysis).toHaveProperty('keyElements');
      expect(analysis).toHaveProperty('characteristics');
      expect(analysis).toHaveProperty('confidenceScore');
    });
  });

  describe('executeSearch', () => {
    it('should return both original source and viral moments', async () => {
      const input: SearchInput = {
        type: 'url',
        content: 'https://twitter.com/user/status/1234567890'
      };

      const results = await searchEngine.executeSearch(input);
      expect(results).toHaveProperty('originalSource');
      expect(results).toHaveProperty('viralMoments');
      expect(results).toHaveProperty('confidenceScore');
    });

    it('should handle cases where no source is found', async () => {
      const input: SearchInput = {
        type: 'url',
        content: 'https://invalid-url.com'
      };

      const results = await searchEngine.executeSearch(input);
      expect(results).toHaveProperty('suggestedSearches');
      expect(results).toHaveProperty('alternativeQueries');
    });
  });
}); 