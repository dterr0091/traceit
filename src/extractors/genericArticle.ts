import Mercury from '@postlight/mercury-parser';
import { Extractor } from './base';
import { ExtractedPost } from '../types/ExtractedPost';

interface MercuryResult {
  title: string | null;
  author: string | null;
  date_published: string | null;
  content: string | null;
  lead_image_url: string | null;
}

export class GenericArticleExtractor extends Extractor {
  static canHandle(url: URL): boolean {
    // Handle any URL that's not handled by other extractors
    // This is a fallback extractor
    return true;
  }

  async extract(url: URL): Promise<ExtractedPost> {
    this.validateUrl(url);

    try {
      const result = await Mercury.parse(url.href) as MercuryResult;

      return {
        platform: 'article',
        url: url.href,
        author: result.author || undefined,
        timestamp: result.date_published ? new Date(result.date_published) : null,
        title: result.title || undefined,
        plainText: result.content || '',
        mediaUrls: result.lead_image_url ? [result.lead_image_url] : undefined
      };
    } catch (error) {
      throw new Error(`Failed to extract article: ${(error as Error).message}`);
    }
  }
} 