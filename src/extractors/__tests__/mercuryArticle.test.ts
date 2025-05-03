import nock from 'nock';
import { MercuryArticleExtractor } from '../mercuryArticle';
import { ContentTooSmallError } from '../../errors/ContentTooSmallError';

describe('MercuryArticleExtractor', () => {
  let extractor: MercuryArticleExtractor;

  beforeEach(() => {
    extractor = new MercuryArticleExtractor();
    nock.cleanAll();
  });

  it('should be eligible for http/https URLs', async () => {
    expect(await extractor.isEligible('http://example.com')).toBe(true);
    expect(await extractor.isEligible('https://example.com')).toBe(true);
    expect(await extractor.isEligible('ftp://example.com')).toBe(false);
  });

  it('should extract article content successfully', async () => {
    const url = 'https://blog.mozilla.org/en/internet/what-is-a-browser/';
    const mockHtml = `
      <html>
        <head>
          <title>What is a Browser?</title>
          <meta name="author" content="Mozilla">
          <meta property="article:published_time" content="2023-01-01T00:00:00Z">
        </head>
        <body>
          <article>
            <h1>What is a Browser?</h1>
            <p>${'A web browser is a software application that enables users to access and view websites on the internet. '.repeat(20)}</p>
            <img src="https://example.com/image.jpg" alt="Browser">
          </article>
        </body>
      </html>
    `;

    nock('https://blog.mozilla.org')
      .get('/en/internet/what-is-a-browser/')
      .reply(200, mockHtml);

    const result = await extractor.extract(url);

    expect(result.platform).toBe('article');
    expect(result.title).toBe('What is a Browser?');
    expect(result.author).toBe('Mozilla');
    expect(result.date_published).toBe('2023-01-01T00:00:00Z');
    expect(result.plainText.length).toBeGreaterThan(1000);
    expect(result.mediaUrls).toEqual(['https://example.com/image.jpg']);
  });

  it('should throw ContentTooSmallError for small content', async () => {
    const url = 'https://example.com';
    const mockHtml = '<html><body><p>Too small</p></body></html>';

    nock('https://example.com')
      .get('/')
      .reply(200, mockHtml);

    await expect(extractor.extract(url)).rejects.toThrow(ContentTooSmallError);
  });
}); 