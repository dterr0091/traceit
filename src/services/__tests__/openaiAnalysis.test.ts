import { OpenAIAnalysisService } from '../openaiAnalysis';
import { ExtractedPost } from '../../types';

jest.mock('openai', () => ({
  OpenAI: jest.fn().mockImplementation(() => ({
    chat: {
      completions: {
        create: jest.fn()
      }
    }
  }))
}));

jest.mock('axios', () => ({
  get: jest.fn()
}));

describe('OpenAIAnalysisService', () => {
  let service: OpenAIAnalysisService;
  const mockTextPost: ExtractedPost = {
    platform: 'article',
    title: 'Test Article',
    author: 'Test Author',
    date_published: '2023-01-01T00:00:00Z',
    content: 'This is a test article about climate change and renewable energy.',
    plainText: 'This is a test article about climate change and renewable energy.',
    mediaUrls: [],
    url: 'https://example.com/article'
  };

  const mockImagePost: ExtractedPost = {
    ...mockTextPost,
    mediaUrls: ['https://example.com/image.jpg']
  };

  beforeEach(() => {
    service = new OpenAIAnalysisService();
    jest.clearAllMocks();
  });

  describe('text analysis', () => {
    it('should analyze text content and generate search queries', async () => {
      const mockResponse = {
        choices: [{
          message: {
            content: JSON.stringify({
              searchQueries: [
                'climate change renewable energy original source',
                'test article climate change first publication',
                'renewable energy article earliest mention'
              ],
              keyTopics: ['climate change', 'renewable energy'],
              suggestedTimeframe: '2020-2023'
            })
          }
        }]
      };

      require('openai').OpenAI.mock.instances[0].chat.completions.create
        .mockResolvedValue(mockResponse);

      const result = await service.analyzeContent(mockTextPost);

      expect(result.searchQueries).toHaveLength(3);
      expect(result.searchQueries[0]).toContain('climate change');
      expect(result.searchQueries[0]).toContain('renewable energy');
      expect(result.keyTopics).toContain('climate change');
      expect(result.suggestedTimeframe).toBe('2020-2023');
      expect(result.imageAnalysis).toBeUndefined();
    });
  });

  describe('vision analysis', () => {
    it('should analyze image content and generate search queries', async () => {
      const mockImageResponse = Buffer.from('mock image data');
      const mockVisionResponse = {
        choices: [{
          message: {
            content: JSON.stringify({
              searchQueries: [
                'climate change protest image original source',
                'environmental demonstration photo first publication',
                'climate activists march earliest photo'
              ],
              keyTopics: ['climate change', 'protest', 'environment'],
              suggestedTimeframe: '2020-2023',
              imageAnalysis: {
                description: 'A large group of people holding signs about climate change',
                objects: ['protest signs', 'crowd', 'banners'],
                text: ['Climate Action Now', 'Save Our Planet']
              }
            })
          }
        }]
      };

      require('axios').get.mockResolvedValue({ data: mockImageResponse });
      require('openai').OpenAI.mock.instances[0].chat.completions.create
        .mockResolvedValue(mockVisionResponse);

      const result = await service.analyzeContent(mockImagePost);

      expect(result.searchQueries).toHaveLength(3);
      expect(result.searchQueries[0]).toContain('climate change');
      expect(result.keyTopics).toContain('climate change');
      expect(result.suggestedTimeframe).toBe('2020-2023');
      expect(result.imageAnalysis).toBeDefined();
      expect(result.imageAnalysis?.description).toContain('group of people');
      expect(result.imageAnalysis?.objects).toContain('protest signs');
      expect(result.imageAnalysis?.text).toContain('Climate Action Now');
    });

    it('should handle image download errors', async () => {
      require('axios').get.mockRejectedValue(new Error('Failed to download image'));

      await expect(service.analyzeContent(mockImagePost))
        .rejects
        .toThrow('Failed to analyze content with OpenAI');
    });
  });

  it('should handle OpenAI API errors gracefully', async () => {
    require('openai').OpenAI.mock.instances[0].chat.completions.create
      .mockRejectedValue(new Error('API Error'));

    await expect(service.analyzeContent(mockTextPost))
      .rejects
      .toThrow('Failed to analyze content with OpenAI');
  });

  it('should validate OpenAI response format', async () => {
    const mockInvalidResponse = {
      choices: [{
        message: {
          content: 'invalid json'
        }
      }]
    };

    require('openai').OpenAI.mock.instances[0].chat.completions.create
      .mockResolvedValue(mockInvalidResponse);

    await expect(service.analyzeContent(mockTextPost))
      .rejects
      .toThrow('Invalid OpenAI response format');
  });
}); 