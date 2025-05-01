import { ContentAnalysisService } from '../contentAnalysis';
import { ContentType } from '../contentAnalysis';

describe('ContentAnalysisService', () => {
  let service: ContentAnalysisService;

  beforeEach(() => {
    service = ContentAnalysisService.getInstance();
  });

  describe('analyzeContent', () => {
    it('should analyze text content correctly', async () => {
      const input = {
        content: 'Sample text content',
        type: 'text' as ContentType,
      };

      const result = await service.analyzeContent(input);

      expect(result).toHaveProperty('type', 'text');
      expect(result).toHaveProperty('keyElements');
      expect(result).toHaveProperty('characteristics');
      expect(result).toHaveProperty('confidence');
      expect(result).toHaveProperty('timestamp');
      expect(result).toHaveProperty('semanticMeaning');
      expect(result).toHaveProperty('entities');
      expect(result).toHaveProperty('topics');
    });

    it('should analyze media content correctly', async () => {
      const input = {
        content: 'https://example.com/image.jpg',
        type: 'image' as ContentType,
      };

      const result = await service.analyzeContent(input);

      expect(result).toHaveProperty('type', 'image');
      expect(result).toHaveProperty('keyElements');
      expect(result).toHaveProperty('characteristics');
      expect(result).toHaveProperty('confidence');
      expect(result).toHaveProperty('timestamp');
      expect(result).toHaveProperty('features');
      expect(result).toHaveProperty('patterns');
    });

    it('should throw error for invalid content type', async () => {
      const input = {
        content: 'Sample content',
        type: 'invalid' as ContentType,
      };

      await expect(service.analyzeContent(input)).rejects.toThrow();
    });

    it('should validate input schema', async () => {
      const input = {
        // Missing required fields
      };

      await expect(service.analyzeContent(input as any)).rejects.toThrow();
    });
  });
}); 