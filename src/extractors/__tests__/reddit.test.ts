import nock from 'nock';
import { RedditExtractor } from '../reddit';

describe('RedditExtractor', () => {
  const testUrl = new URL('https://www.reddit.com/r/aww/comments/kv8q8d/');
  const mockResponse = [{
    data: {
      children: [{
        data: {
          title: 'Test Post',
          author: 'testuser',
          selftext: 'Test content',
          created_utc: 1610410000,
          url: 'https://www.reddit.com/r/aww/comments/kv8q8d/',
          is_video: false,
          preview: {
            images: [{
              source: {
                url: 'https://test-image.jpg'
              }
            }]
          }
        }
      }]
    }
  }];

  beforeEach(() => {
    nock.cleanAll();
  });

  it('should correctly identify Reddit URLs', () => {
    expect(RedditExtractor.canHandle(new URL('https://www.reddit.com/r/test'))).toBe(true);
    expect(RedditExtractor.canHandle(new URL('https://reddit.com/r/test'))).toBe(true);
    expect(RedditExtractor.canHandle(new URL('https://other.com'))).toBe(false);
  });

  it('should extract post data correctly', async () => {
    nock('https://www.reddit.com')
      .get('/comments/kv8q8d.json')
      .reply(200, mockResponse);

    const extractor = new RedditExtractor();
    const result = await extractor.extract(testUrl);

    expect(result).toEqual({
      platform: 'reddit',
      url: testUrl.href,
      author: 'testuser',
      timestamp: new Date(1610410000 * 1000),
      title: 'Test Post',
      plainText: 'Test content',
      mediaUrls: ['https://test-image.jpg']
    });
  });

  it('should handle invalid Reddit URLs', async () => {
    const extractor = new RedditExtractor();
    await expect(
      extractor.extract(new URL('https://www.reddit.com/invalid'))
    ).rejects.toThrow('Invalid Reddit URL format');
  });

  it('should handle API errors', async () => {
    nock('https://www.reddit.com')
      .get('/comments/kv8q8d.json')
      .reply(500);

    const extractor = new RedditExtractor();
    await expect(
      extractor.extract(testUrl)
    ).rejects.toThrow();
  });
}); 