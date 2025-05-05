import { SearchService, quotaStore } from '../searchService';
import { PerplexityService } from '../perplexity';
import { RedisService } from '../redisService';
import { ExtractedPost } from '../../types/index';
import { Thought, PrimaryThought } from '../../types/thoughts';
import OpenAI from 'openai';

// Mock the dependencies
jest.mock('openai');
jest.mock('../perplexity');
jest.mock('../redisService');
jest.mock('uuid', () => ({
  v4: jest.fn().mockReturnValue('test-uuid-123')
}));

// Reset the quotaStore for testing
const resetQuotaStore = () => {
  // Clear all properties from the quotaStore
  Object.keys(quotaStore).forEach(key => {
    delete quotaStore[key];
  });
};

describe('SearchService', () => {
  let searchService: SearchService;
  let mockOpenAI: any;
  let mockPerplexity: jest.Mocked<PerplexityService>;
  let mockRedis: jest.Mocked<RedisService>;

  // Sample test data
  const userId = 'test-user-1';
  const samplePost: ExtractedPost = {
    platform: 'article',
    url: 'https://example.com/test-article',
    author: 'Test Author',
    title: 'Test Article Title',
    plainText: 'This is a test article with some interesting claims and facts.',
    mediaUrls: ['https://example.com/test-image.jpg'],
    date_published: '2023-05-01',
    content: 'This is a test article with some interesting claims and facts.'
  };

  const mockEmbedding = [0.1, 0.2, 0.3, 0.4];
  
  const mockThoughts: Thought[] = [
    {
      id: 'test-uuid-123',
      content: 'This is the primary thought',
      embedding: mockEmbedding,
      score: 90
    },
    {
      id: 'test-uuid-456',
      content: 'This is a secondary thought 1',
      embedding: mockEmbedding,
      score: 70
    },
    {
      id: 'test-uuid-789',
      content: 'This is a secondary thought 2',
      embedding: mockEmbedding,
      score: 60
    }
  ];
  
  const mockPrimaryThought: PrimaryThought = {
    ...mockThoughts[0],
    origin: 'Test Source',
    viral: true,
    evidence: [
      {
        url: 'https://example.com/evidence1',
        title: 'Evidence 1',
        snippet: 'This is a relevant evidence snippet'
      }
    ]
  };

  beforeEach(() => {
    jest.clearAllMocks();
    resetQuotaStore();
    
    // Setup mock OpenAI
    mockOpenAI = {
      chat: {
        completions: {
          create: jest.fn()
        }
      },
      embeddings: {
        create: jest.fn()
      }
    };
    
    // Mock OpenAI constructor
    (OpenAI as jest.MockedClass<typeof OpenAI>).mockImplementation(() => mockOpenAI);
    
    // Mock OpenAI responses
    mockOpenAI.chat.completions.create.mockImplementation((params: any) => {
      if (params.messages[0].content.includes('extracts key thoughts')) {
        return Promise.resolve({
          choices: [{ message: { content: '1. This is the primary thought\n2. This is a secondary thought 1\n3. This is a secondary thought 2' } }]
        });
      } else if (params.messages[0].content.includes('ranks thoughts')) {
        return Promise.resolve({
          choices: [{ message: { content: JSON.stringify({ scores: [90, 70, 60] }) } }]
        });
      } else if (params.messages[0].content.includes('analyze search results')) {
        return Promise.resolve({
          choices: [{ message: { content: JSON.stringify({ origin: 'Test Source', viral: true }) } }]
        });
      }
      return Promise.resolve({ choices: [{ message: { content: 'Default mock response' } }] });
    });
    
    mockOpenAI.embeddings.create.mockResolvedValue({
      data: [{ embedding: mockEmbedding }]
    });
    
    // Setup mock Perplexity
    mockPerplexity = {
      search: jest.fn().mockResolvedValue([
        {
          url: 'https://example.com/evidence1',
          title: 'Evidence 1',
          snippet: 'This is a relevant evidence snippet'
        }
      ])
    } as any;
    
    // Setup mock Redis
    mockRedis = {
      storeThought: jest.fn().mockResolvedValue(undefined),
      storeSecondaryThoughts: jest.fn().mockResolvedValue(undefined),
      getSecondaryThoughts: jest.fn().mockResolvedValue([mockThoughts[1], mockThoughts[2]])
    } as any;
    
    // Inject mocks
    (PerplexityService as jest.MockedClass<typeof PerplexityService>).mockImplementation(() => mockPerplexity);
    (RedisService as jest.MockedClass<typeof RedisService>).mockImplementation(() => mockRedis);
    
    // Initialize the service
    searchService = new SearchService();
  });

  describe('traceSearch', () => {
    it('should process a post through all stages and return the lineage', async () => {
      const result = await searchService.traceSearch(userId, samplePost);
      
      // Assert result structure
      expect(result).toHaveProperty('primaryThought');
      expect(result).toHaveProperty('secondaryCount');
      expect(result.secondaryCount).toBe(2);
      
      // Verify each stage was called
      expect(mockOpenAI.chat.completions.create).toHaveBeenCalledTimes(3);
      expect(mockOpenAI.embeddings.create).toHaveBeenCalledTimes(3);
      expect(mockPerplexity.search).toHaveBeenCalledTimes(1);
      expect(mockRedis.storeThought).toHaveBeenCalledTimes(1);
      expect(mockRedis.storeSecondaryThoughts).toHaveBeenCalledTimes(1);
    });
    
    it('should throw an error when quota is exceeded', async () => {
      // Mock the quotaStore to simulate quota exceeded
      Object.defineProperty(searchService, 'quotaGuard', {
        value: jest.fn().mockResolvedValue(false)
      });
      
      // The call should fail due to quota
      await expect(searchService.traceSearch(userId, samplePost)).rejects.toThrow('Daily search quota exceeded');
    });
  });

  describe('legacy search interface', () => {
    it('should call the correct search method based on inputs', async () => {
      // Mock the original methods first
      const originalLegacySearch = (searchService as any).legacySearch;
      const originalTraceSearch = searchService.traceSearch;
      
      // Create mock implementations that our spies will use
      const mockLegacySearch = jest.fn().mockResolvedValue([]);
      const mockTraceSearch = jest.fn().mockResolvedValue({ 
        primaryThought: mockPrimaryThought, 
        secondaryCount: 2 
      });
      
      // Replace the methods with our mocks
      (searchService as any).legacySearch = mockLegacySearch;
      searchService.traceSearch = mockTraceSearch;
      
      // Call with legacy interface
      await searchService.search({ text: 'test query' });
      expect(mockLegacySearch).toHaveBeenCalledTimes(1);
      expect(mockTraceSearch).toHaveBeenCalledTimes(0);
      
      // Reset the mock counts
      mockLegacySearch.mockClear();
      mockTraceSearch.mockClear();
      
      // Call with new interface
      await searchService.search(userId, samplePost);
      expect(mockLegacySearch).toHaveBeenCalledTimes(0);
      expect(mockTraceSearch).toHaveBeenCalledTimes(1);
      
      // Restore the original methods
      (searchService as any).legacySearch = originalLegacySearch;
      searchService.traceSearch = originalTraceSearch;
    });
  });
  
  describe('getSecondaryThoughts', () => {
    it('should retrieve secondary thoughts from Redis', async () => {
      const thoughts = await searchService.getSecondaryThoughts('test-primary-id');
      
      expect(mockRedis.getSecondaryThoughts).toHaveBeenCalledWith('test-primary-id');
      expect(thoughts).toHaveLength(2);
      expect(thoughts[0].content).toBe('This is a secondary thought 1');
    });
  });
}); 