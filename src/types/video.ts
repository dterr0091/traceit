export interface VideoMetadata {
  title: string;
  description: string;
  duration: number;
  thumbnailUrl: string;
  publishedAt: string;
  platform: string;
  platformSpecificData?: Record<string, any>;
} 