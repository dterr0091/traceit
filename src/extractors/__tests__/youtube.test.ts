import { execFile } from 'child_process';
import { YouTubeExtractor } from '../youtube';

jest.mock('child_process');

describe('YouTubeExtractor', () => {
  const testUrl = new URL('https://www.youtube.com/watch?v=dQw4w9WgXcQ');
  const mockYtDlpOutput = {
    title: 'Never Gonna Give You Up',
    uploader: 'Rick Astley',
    upload_date: '20090225',
    description: 'Official music video',
    thumbnail: 'https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg'
  };

  beforeEach(() => {
    jest.resetAllMocks();
    (execFile as jest.Mock).mockImplementation((_, __, callback) => {
      callback(null, { stdout: JSON.stringify(mockYtDlpOutput) });
    });
  });

  it('should correctly identify YouTube URLs', () => {
    expect(YouTubeExtractor.canHandle(new URL('https://www.youtube.com/watch?v=123'))).toBe(true);
    expect(YouTubeExtractor.canHandle(new URL('https://youtube.com/watch?v=123'))).toBe(true);
    expect(YouTubeExtractor.canHandle(new URL('https://youtu.be/123'))).toBe(true);
    expect(YouTubeExtractor.canHandle(new URL('https://other.com'))).toBe(false);
  });

  it('should extract video data correctly', async () => {
    const extractor = new YouTubeExtractor();
    const result = await extractor.extract(testUrl);

    expect(result).toEqual({
      platform: 'youtube',
      url: testUrl.href,
      author: 'Rick Astley',
      timestamp: new Date(2009, 1, 25), // February 25, 2009
      title: 'Never Gonna Give You Up',
      plainText: 'Official music video',
      mediaUrls: ['https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg']
    });
  });

  it('should handle yt-dlp errors', async () => {
    (execFile as jest.Mock).mockImplementation((_, __, callback) => {
      callback(new Error('yt-dlp failed'));
    });

    const extractor = new YouTubeExtractor();
    await expect(
      extractor.extract(testUrl)
    ).rejects.toThrow('Failed to extract YouTube video');
  });
}); 