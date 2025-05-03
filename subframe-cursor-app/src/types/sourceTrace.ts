export interface SearchResult {
  title: string;
  platform: string;
  timestamp: string;
  viralityScore: 'High' | 'Medium' | 'Low';
  platformIcon: string;
  isOriginalSource: boolean;
  sourceIndex?: number;
}

export interface SearchState {
  isLoading: boolean;
  currentStep: string;
  error: string | null;
  results: SearchResult[] | null;
}

export interface CommunityNote {
  id: number;
  user: {
    name: string;
    avatar: string;
    badge: string;
  };
  content: string;
  helpfulCount: number;
  timestamp: string;
}

export interface PerplexitySearchResult {
  title: string;
  url: string;
  snippet: string;
  timestamp: string;
  platform: string;
  engagement_metrics: {
    likes?: number;
    shares?: number;
    comments?: number;
    views?: number;
  };
}

export interface PerplexitySearchResponse {
  results: PerplexitySearchResult[];
  total_results: number;
  query_time: number;
}

export interface SearchInput {
  text?: string;
  image_urls?: string[];
  urls?: string[];
  max_results?: number;
}

export interface SearchService {
  search(input: SearchInput): Promise<PerplexitySearchResult[]>;
} 