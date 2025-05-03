export type Platform = 'reddit' | 'youtube' | 'x' | 'tiktok' | 'instagram' | 'article' | 'unknown';

export interface ExtractedPost {
  platform: Platform;
  url: string;
  author?: string;
  timestamp: Date | null;
  title?: string;
  plainText: string;          // caption, body, or transcript
  mediaUrls?: string[];       // direct links to images / videos / thumbnails
}

export class UnsupportedInputError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'UnsupportedInputError';
  }
} 