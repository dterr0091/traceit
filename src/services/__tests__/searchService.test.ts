import { SearchService } from '../searchService';
import { ExtractedPost } from '../../types';
import { OpenAIAnalysisService } from '../openaiAnalysis';

jest.mock('../openaiAnalysis');
jest.mock('axios');

describe('SearchService', () => {
  let service: SearchService;
  const mockExtractedPost: ExtractedPost = {
    platform: 'article',
    title: 'Test Article',
    author: 'Test Author',
    date_published: '2023-01-01T00:00:00Z',
    content: 'This is a test article about climate change and renewable energy.',
    plainText: 'This is a test article about climate change and renewable energy.',
    mediaUrls: [],
    url: 'https://example.com/article'
  };

  beforeEach(() => {
    service = new SearchService();
    jest.clearAllMocks();
  });

  describe('analyzeAndSearch', () => {
    it('should analyze content and perform search', async () => {
      const mockAnalysis = {
        searchQueries: ['climate change renewable energy original source'],
        keyTopics: ['climate change', 'renewable energy'],
        suggestedTimeframe: '2020-2023'
      };

      const mockSearchResults = [{
        url: 'https://example.com/original',
        title: 'Original Article',
        snippet: 'This is the original article about climate change',
        published_date: '2020-01-01'
      }];

      (OpenAIAnalysisService.prototype.analyzeContent as jest.Mock)
        .mockResolvedValue(mockAnalysis);

      require('axios').post.mockResolvedValue({
        data: { results: mockSearchResults }
      });

      const results = await service.analyzeAndSearch(mockExtractedPost);

      expect(results).toEqual(mockSearchResults);
      expect(OpenAIAnalysisService.prototype.analyzeContent)
        .toHaveBeenCalledWith(mockExtractedPost);
    });

    it('should handle OpenAI analysis errors', async () => {
      (OpenAIAnalysisService.prototype.analyzeContent as jest.Mock)
        .mockRejectedValue(new Error('Analysis failed'));

      await expect(service.analyzeAndSearch(mockExtractedPost))
        .rejects
        .toThrow('Failed to analyze and search content');
    });

    it('should handle Perplexity API errors', async () => {
      const mockAnalysis = {
        searchQueries: ['climate change renewable energy original source'],
        keyTopics: ['climate change', 'renewable energy'],
        suggestedTimeframe: '2020-2023'
      };

      (OpenAIAnalysisService.prototype.analyzeContent as jest.Mock)
        .mockResolvedValue(mockAnalysis);

      require('axios').post.mockRejectedValue(new Error('API Error'));

      await expect(service.analyzeAndSearch(mockExtractedPost))
        .rejects
        .toThrow('Failed to analyze and search content');
    });
  });
}); 