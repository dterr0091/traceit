import puppeteer from 'puppeteer-core';
import Mercury from '@postlight/mercury-parser';
import { Extractor } from './base';
import { ExtractedPost } from '../types';
import chromium from '@sparticuz/chromium';

export class HeadlessExtractor extends Extractor {

  async isEligible(url: string): Promise<boolean> {
    // Handle any URL that requires JS rendering
    // Logic to determine eligibility might be more complex in a real scenario
    return url.startsWith('http://') || url.startsWith('https://'); 
  }

  static canHandle(url: URL): boolean {
    // This is a fallback extractor for JavaScript-heavy sites
    // that need rendering
    return true;
  }

  async extract(url: string): Promise<ExtractedPost> {
    const urlObj = new URL(url);
    this.validateUrl(urlObj);

    const executablePath = await chromium.executablePath(
      process.env.CHROMIUM_EXECUTABLE_PATH || undefined
    );

    const browser = await puppeteer.launch({
      args: chromium.args,
      executablePath,
      headless: true, // Set to boolean true
      ignoreHTTPSErrors: true,
      defaultViewport: { width: 1280, height: 800 }
    });

    try {
      const page = await browser.newPage();
      await page.goto(url, { waitUntil: 'networkidle0' });
      
      const html = await page.evaluate(() => {
        return document.documentElement.outerHTML;
      });

      const result = await Mercury.parse(url, { html });

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
      throw new Error(`Failed to extract with headless browser: ${error instanceof Error ? error.message : String(error)}`);
    } finally {
      await browser.close();
    }
  }
} 