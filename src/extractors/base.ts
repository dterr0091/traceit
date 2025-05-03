import { ExtractedPost } from '../types';
import { Extractor as ExtractorInterface } from '../types';

export abstract class Extractor implements ExtractorInterface {
  /**
   * Check if this extractor can handle the given URL
   */
  static canHandle(url: URL): boolean {
    throw new Error('canHandle() must be implemented by subclass');
  }

  /**
   * Extract content from the given URL and return structured data
   */
  abstract extract(url: string): Promise<ExtractedPost>;

  /**
   * Helper method to validate URL format
   */
  protected validateUrl(url: URL): void {
    if (!url || typeof url.href !== 'string') {
      throw new Error('Invalid URL provided');
    }
  }

  abstract isEligible(url: string): Promise<boolean>;
} 