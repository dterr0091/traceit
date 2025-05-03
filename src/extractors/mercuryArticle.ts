import axios from 'axios';
import { parse } from '@postlight/mercury-parser';
import { Extractor } from './base';
import { ExtractedPost } from '../types';
import { ContentTooSmallError } from '../errors/ContentTooSmallError';

export class MercuryArticleExtractor extends Extractor {
  async isEligible(url: string): Promise<boolean> {
    return url.startsWith('http://') || url.startsWith('https://');
  }

  async extract(url: string): Promise<ExtractedPost> {
    try {
      const response = await axios.get(url);
      const html = response.data;
      
      if (html.length < 1024) {
        throw new ContentTooSmallError();
      }

      const result = await parse(url, { html });
      
      if (!result.content || result.content.length < 100) {
        throw new ContentTooSmallError();
      }

      return {
        platform: 'article',
        title: result.title || '',
        author: result.author || '',
        date_published: result.date_published || new Date().toISOString(),
        content: result.content,
        plainText: result.content,
        mediaUrls: result.lead_image_url ? [result.lead_image_url] : [],
        url
      };
    } catch (error) {
      if (error instanceof ContentTooSmallError) {
        throw error;
      }
      throw new Error(`Failed to extract article: ${error.message}`);
    }
  }
} 