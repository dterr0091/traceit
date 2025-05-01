import { SearchInput, ViralMoment } from '../types';

export interface PlatformSearchResult {
  originalSource?: {
    url: string;
    timestamp: string;
    platform: string;
    confidenceScore: number;
  };
  viralMoments: ViralMoment[];
  confidenceScore: number;
}

export interface PlatformSearcher {
  platform: string;
  canHandle(input: SearchInput): Promise<boolean>;
  search(input: SearchInput, analysis: any): Promise<PlatformSearchResult>;
} 