import { HeadlessFallbackExtractor } from '../headlessFallback';
import { ContentTooSmallError } from '../../errors/ContentTooSmallError';

jest.mock('puppeteer-core');
jest.mock('@postlight/mercury-parser');
jest.mock('@sparticuz/chromium');

describe('HeadlessFallbackExtractor', () => {
  let extractor: HeadlessFallbackExtractor;

  beforeEach(() => {
    extractor = new HeadlessFallbackExtractor();
    jest.clearAllMocks();
  });

  it('should be eligible for http/https URLs', async () => {
    expect(await extractor.isEligible('http://example.com')).toBe(true);
    expect(await extractor.isEligible('https://example.com')).toBe(true);
    expect(await extractor.isEligible('ftp://example.com')).toBe(false);
  });

  it('should extract article content successfully', async () => {
    const urlString = 'https://example.com';
    const url = new URL(urlString);
    const mockHtml = `
      <html>
        <head>
          <title>Test Article</title>
          <meta name="author" content="Test Author">
          <meta property="article:published_time" content="2023-01-01T00:00:00Z">
        </head>
        <body>
          <article>
            <h1>Test Article</h1>
            <p>${'This is a test article content. '.repeat(20)}</p>
            <img src="https://example.com/image.jpg" alt="Test">
          </article>
        </body>
      </html>
    `;

    const mockPage = {
      goto: jest.fn().mockResolvedValue(null),
      content: jest.fn().mockResolvedValue(mockHtml),
      close: jest.fn()
    };

    const mockBrowser = {
      newPage: jest.fn().mockResolvedValue(mockPage),
      close: jest.fn()
    };

    require('puppeteer-core').launch.mockResolvedValue(mockBrowser);
    require('@postlight/mercury-parser').parse.mockResolvedValue({
      title: 'Test Article',
      author: 'Test Author',
      date_published: '2023-01-01T00:00:00Z',
      content: 'This is a test article content. '.repeat(20),
      lead_image_url: 'https://example.com/image.jpg'
    });

    const result = await extractor.extract(url);

    expect(result.platform).toBe('article');
    expect(result.title).toBe('Test Article');
    expect(result.author).toBe('Test Author');
    expect(result.timestamp).toEqual(new Date('2023-01-01T00:00:00Z'));
    expect(result.plainText.length).toBeGreaterThan(1000);
    expect(result.mediaUrls).toEqual(['https://example.com/image.jpg']);
  });

  it('should throw ContentTooSmallError for small content', async () => {
    const urlString = 'https://example.com';
    const url = new URL(urlString);
    const mockHtml = '<html><body><p>Too small</p></body></html>';

    const mockPage = {
      goto: jest.fn().mockResolvedValue(null),
      content: jest.fn().mockResolvedValue(mockHtml),
      close: jest.fn()
    };

    const mockBrowser = {
      newPage: jest.fn().mockResolvedValue(mockPage),
      close: jest.fn()
    };

    require('puppeteer-core').launch.mockResolvedValue(mockBrowser);

    await expect(extractor.extract(url)).rejects.toThrow(ContentTooSmallError);
  });
}); 