import { ContentAnalysisService, contentInputSchema, ContentType } from '@/services/contentAnalysis';
import { z } from 'zod';

describe('ContentAnalysisService', () => {
  let service: ContentAnalysisService;

  beforeEach(() => {
    service = ContentAnalysisService.getInstance();
  });

  describe('getInstance', () => {
    it('should return the same instance on multiple calls', () => {
      const instance1 = ContentAnalysisService.getInstance();
      const instance2 = ContentAnalysisService.getInstance();
      expect(instance1).toBe(instance2);
    });
  });

  describe('contentInputSchema', () => {
    it('should validate correct input', () => {
      const validInput = {
        content: 'https://example.com/image.jpg',
        type: 'image' as ContentType,
        metadata: { size: 'large' }
      };
      expect(() => contentInputSchema.parse(validInput)).not.toThrow();
    });

    it('should reject invalid content type', () => {
      const invalidInput = {
        content: 'https://example.com/image.jpg',
        type: 'invalid_type' as any,
        metadata: { size: 'large' }
      };
      expect(() => contentInputSchema.parse(invalidInput)).toThrow();
    });

    it('should accept input without metadata', () => {
      const inputWithoutMetadata = {
        content: 'https://example.com/image.jpg',
        type: 'image' as ContentType
      };
      expect(() => contentInputSchema.parse(inputWithoutMetadata)).not.toThrow();
    });
  });

  describe('analyzeContent', () => {
    it('should route image content to analyzeMedia', async () => {
      const input = {
        content: 'https://example.com/image.jpg',
        type: 'image' as ContentType
      };
      const result = await service.analyzeContent(input);
      expect(result.type).toBe('image');
      expect(result).toHaveProperty('features');
      expect(result).toHaveProperty('patterns');
    });

    it('should route text content to analyzeText', async () => {
      const input = {
        content: 'Sample text content',
        type: 'text' as ContentType
      };
      const result = await service.analyzeContent(input);
      expect(result.type).toBe('text');
      expect(result).toHaveProperty('semanticMeaning');
      expect(result).toHaveProperty('entities');
      expect(result).toHaveProperty('topics');
    });

    it('should throw error for unsupported content type', async () => {
      const input = {
        content: 'https://example.com/file.xyz',
        type: 'unsupported' as any
      };
      await expect(service.analyzeContent(input)).rejects.toThrow();
    });
  });

  describe('parseMediaAnalysis', () => {
    it('should parse media analysis results correctly', () => {
      const analysis = `
        Key visual elements: landscape, sunset
        Features: high contrast, warm colors
        Patterns: repeating clouds, gradient sky
        Characteristics: format=jpg, resolution=1920x1080
      `;
      const result = service['parseMediaAnalysis'](analysis);
      expect(result).toHaveProperty('keyElements');
      expect(result).toHaveProperty('features');
      expect(result).toHaveProperty('patterns');
      expect(result).toHaveProperty('characteristics');
      expect(result).toHaveProperty('confidence');
    });
  });

  describe('parseTextAnalysis', () => {
    it('should parse text analysis results correctly', () => {
      const analysis = `
        Semantic meaning: Discussion about climate change
        Key elements: global warming, carbon emissions
        Entities: IPCC, United Nations
        Topics: environment, policy
        Characteristics: language=English, length=medium
      `;
      const result = service['parseTextAnalysis'](analysis);
      expect(result).toHaveProperty('semanticMeaning');
      expect(result).toHaveProperty('keyElements');
      expect(result).toHaveProperty('entities');
      expect(result).toHaveProperty('topics');
      expect(result).toHaveProperty('characteristics');
      expect(result).toHaveProperty('confidence');
    });
  });
}); 