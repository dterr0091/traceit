export type SearchInputType = 'url' | 'text' | 'media';

export interface SearchInput {
  type: SearchInputType;
  content: string;
}

export interface ContentAnalysis {
  keyElements: string[];
  characteristics: Record<string, any>;
  confidenceScore: number;
}

export interface ViralMoment {
  url: string;
  timestamp: string;
  platform: string;
  metrics?: {
    views?: number;
    shares?: number;
    likes?: number;
  };
}

export interface SearchResult {
  originalSource?: {
    url: string;
    timestamp: string;
    platform: string;
    confidenceScore: number;
  };
  viralMoments: ViralMoment[];
  confidenceScore: number;
  suggestedSearches?: string[];
  alternativeQueries?: string[];
} 