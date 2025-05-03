import Mercury from '@postlight/mercury-parser';
import { Extractor } from './base';
import { ExtractedPost } from '../types';
import { ContentTooSmallError } from '../errors/ContentTooSmallError';

interface MercuryResult {
  title: string | null;
  author: string | null;
  date_published: string | null;
  content: string | null;
  lead_image_url: string | null;
}

export class MercuryArticleExtractor extends Extractor {
  static canHandle(url: URL): boolean {
    // Assuming it can handle general article-like URLs
    return true;
  }

  async isEligible(url: string): Promise<boolean> {
    // Assuming eligibility for any http/https URL as a generic article extractor
    return url.startsWith('http://') || url.startsWith('https://');
  }

  async extract(url: string): Promise<ExtractedPost> {
    const urlObj = new URL(url);
    this.validateUrl(urlObj);

    try {
      const result = await Mercury.parse(url) as MercuryResult;

      return {
        platform: 'article',
        url: url,
        author: result.author || '',
        date_published: result.date_published || new Date().toISOString(),
        title: result.title || '',
        content: result.content || '',
        plainText: result.content || '',
        mediaUrls: result.lead_image_url ? [result.lead_image_url] : []
      };
    } catch (error) {
      throw new Error(`Failed to extract article with Mercury: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
} 