import Mercury from '@postlight/mercury-parser';
import { GenericArticleExtractor } from '../genericArticle';

jest.mock('@postlight/mercury-parser');

describe('GenericArticleExtractor', () => {
  const testUrl = new URL('https://blog.mozilla.org/en/internet/what-is-a-browser/');
  const mockMercuryResult = {
    title: 'What is a browser?',
    author: 'Mozilla',
    date_published: '2023-01-15T12:00:00.000Z',
    content: 'A web browser is software that allows you to access websites.',
    lead_image_url: 'https://blog.mozilla.org/browser-image.jpg'
  };

  beforeEach(() => {
    jest.resetAllMocks();
    (Mercury.parse as jest.Mock).mockResolvedValue(mockMercuryResult);
  });

  it('should handle any URL', () => {
    expect(GenericArticleExtractor.canHandle(new URL('https://any-url.com'))).toBe(true);
  });

  it('should extract article data correctly', async () => {
    const extractor = new GenericArticleExtractor();
    const result = await extractor.extract(testUrl);

    expect(result).toEqual({
      platform: 'article',
      url: testUrl.href,
      author: 'Mozilla',
      timestamp: new Date('2023-01-15T12:00:00.000Z'),
      title: 'What is a browser?',
      plainText: 'A web browser is software that allows you to access websites.',
      mediaUrls: ['https://blog.mozilla.org/browser-image.jpg']
    });
  });

  it('should handle missing fields gracefully', async () => {
    (Mercury.parse as jest.Mock).mockResolvedValue({
      title: null,
      author: null,
      date_published: null,
      content: null,
      lead_image_url: null
    });

    const extractor = new GenericArticleExtractor();
    const result = await extractor.extract(testUrl);

    expect(result).toEqual({
      platform: 'article',
      url: testUrl.href,
      author: undefined,
      timestamp: null,
      title: undefined,
      plainText: '',
      mediaUrls: undefined
    });
  });

  it('should handle Mercury parser errors', async () => {
    (Mercury.parse as jest.Mock).mockRejectedValue(new Error('Parser failed'));

    const extractor = new GenericArticleExtractor();
    await expect(
      extractor.extract(testUrl)
    ).rejects.toThrow('Failed to extract article');
  });
}); 