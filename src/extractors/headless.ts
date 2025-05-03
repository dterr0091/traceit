import puppeteer from 'puppeteer-core';
import Mercury from '@postlight/mercury-parser';
import { Extractor } from './base';
import { ExtractedPost } from '../types/ExtractedPost';

export class HeadlessExtractor extends Extractor {
  private chromiumPath: string;

  constructor() {
    super();
    this.chromiumPath = process.env.CHROMIUM_PATH || '';
    if (!this.chromiumPath) {
      throw new Error('CHROMIUM_PATH environment variable is not set');
    }
  }

  static canHandle(url: URL): boolean {
    // This is a fallback extractor for JavaScript-heavy sites
    // that need rendering
    return true;
  }

  async extract(url: URL): Promise<ExtractedPost> {
    this.validateUrl(url);

    const browser = await puppeteer.launch({
      executablePath: this.chromiumPath,
      headless: 'new'
    });

    try {
      const page = await browser.newPage();
      await page.goto(url.href, { waitUntil: 'networkidle0' });
      
      const html = await page.evaluate(() => {
        return document.documentElement.outerHTML;
      });

      const result = await Mercury.parse(url.href, { html });

      return {
        platform: 'article',
        url: url.href,
        author: result.author || undefined,
        timestamp: result.date_published ? new Date(result.date_published) : null,
        title: result.title || undefined,
        plainText: result.content || '',
        mediaUrls: result.lead_image_url ? [result.lead_image_url] : undefined
      };
    } finally {
      await browser.close();
    }
  }
} 