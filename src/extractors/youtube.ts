import { execFile } from 'child_process';
import { promisify } from 'util';
import { Extractor } from './base';
import { ExtractedPost } from '../types';

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
  private ytdlpAvailable: boolean;

  constructor() {
    super();
    this.ytdlpPath = process.env.YTDLP_BINARY || 'yt-dlp';
    // Check if yt-dlp is available
    this.ytdlpAvailable = this.checkYtDlpAvailability();
  }

  private checkYtDlpAvailability(): boolean {
    try {
      // Try to dynamically load the yt-dlp-exec package
      require('yt-dlp-exec');
      return true;
    } catch (error) {
      console.warn('yt-dlp-exec not available: YouTube extraction might be limited');
      return false;
    }
  }

  static canHandle(url: URL): boolean {
    return url.hostname === 'youtube.com' || 
           url.hostname === 'www.youtube.com' || 
           url.hostname === 'youtu.be';
  }

  async extract(url: string): Promise<ExtractedPost> {
    const urlObj = new URL(url);
    this.validateUrl(urlObj);

    if (!this.ytdlpAvailable) {
      // Fallback when yt-dlp is not available
      return {
        platform: 'youtube',
        url: url,
        author: '',
        date_published: new Date().toISOString(),
        content: '',
        title: 'YouTube video (yt-dlp not available)',
        plainText: `Unable to extract content from ${url} - yt-dlp not available`,
        mediaUrls: []
      };
    }

    try {
      const { stdout } = await execFileAsync(this.ytdlpPath, [
        '--dump-json',
        '--no-download',
        url
      ]);

      const data = JSON.parse(stdout) as YTDLPOutput;
      
      // Convert YYYYMMDD to ISO date string
      const date_published = data.upload_date ? 
        `${data.upload_date.slice(0, 4)}-${data.upload_date.slice(4, 6)}-${data.upload_date.slice(6, 8)}T00:00:00Z` : 
        new Date().toISOString();

      return {
        platform: 'youtube',
        url: url,
        author: data.uploader || '',
        date_published,
        title: data.title || '',
        content: data.description || '',
        plainText: data.description || data.title || '',
        mediaUrls: data.thumbnail ? [data.thumbnail] : []
      };
    } catch (error) {
      throw new Error(`Failed to extract YouTube video: ${(error as Error).message}`);
    }
  }

  async isEligible(url: string): Promise<boolean> {
    try {
      const urlObj = new URL(url);
      return YouTubeExtractor.canHandle(urlObj);
    } catch {
      return false;
    }
  }
} 