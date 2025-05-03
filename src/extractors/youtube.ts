import { execFile } from 'child_process';
import { promisify } from 'util';
import { Extractor } from './base';
import { ExtractedPost } from '../types/ExtractedPost';

const execFileAsync = promisify(execFile);

interface YTDLPOutput {
  title: string;
  uploader: string;
  upload_date: string; // YYYYMMDD format
  description: string;
  thumbnail: string;
}

export class YouTubeExtractor extends Extractor {
  private ytdlpPath: string;

  constructor() {
    super();
    this.ytdlpPath = process.env.YTDLP_BINARY || 'yt-dlp';
  }

  static canHandle(url: URL): boolean {
    return url.hostname === 'youtube.com' || 
           url.hostname === 'www.youtube.com' || 
           url.hostname === 'youtu.be';
  }

  async extract(url: URL): Promise<ExtractedPost> {
    this.validateUrl(url);

    try {
      const { stdout } = await execFileAsync(this.ytdlpPath, [
        '--dump-json',
        '--no-download',
        url.href
      ]);

      const data = JSON.parse(stdout) as YTDLPOutput;
      
      // Convert YYYYMMDD to Date
      const timestamp = data.upload_date ? 
        new Date(
          parseInt(data.upload_date.slice(0, 4)), // year
          parseInt(data.upload_date.slice(4, 6)) - 1, // month (0-based)
          parseInt(data.upload_date.slice(6, 8)) // day
        ) : null;

      return {
        platform: 'youtube',
        url: url.href,
        author: data.uploader,
        timestamp,
        title: data.title,
        plainText: data.description || data.title,
        mediaUrls: data.thumbnail ? [data.thumbnail] : undefined
      };
    } catch (error) {
      throw new Error(`Failed to extract YouTube video: ${(error as Error).message}`);
    }
  }
} 