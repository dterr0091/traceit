import puppeteer from 'puppeteer-core';
import { parse } from '@postlight/mercury-parser';
import { Extractor } from './base';
import { ExtractedPost } from '../types';
import { ContentTooSmallError } from '../errors/ContentTooSmallError';
import chromium from '@sparticuz/chromium';

export class HeadlessFallbackExtractor extends Extractor {
  async isEligible(url: string): Promise<boolean> {
    return url.startsWith('http://') || url.startsWith('https://');
  }

  async extract(url: string): Promise<ExtractedPost> {
    const executablePath = await chromium.executablePath(
      process.env.CHROMIUM_EXECUTABLE_PATH || undefined
    );

    const browser = await puppeteer.launch({
      args: chromium.args,
      executablePath,
      headless: true,
      ignoreHTTPSErrors: true,
      defaultViewport: { width: 1280, height: 800 }
    });

    try {
      const page = await browser.newPage();
      await page.goto(url, {
        waitUntil: 'networkidle0',
        timeout: parseInt(process.env.HEADLESS_TIMEOUT_MS || '20000')
      });

      const html = await page.content();
      await browser.close();

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
        content: result.content || '',
        plainText: result.content || '',
        mediaUrls: result.lead_image_url ? [result.lead_image_url] : [],
        url: url
      };
    } catch (error: unknown) {
      await browser.close();
      if (error instanceof ContentTooSmallError) {
        throw error;
      }
      throw new Error(`Failed to extract article with headless browser: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
} 