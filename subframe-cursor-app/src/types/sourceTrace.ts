export interface SearchResult {
  title: string;
  platform: string;
  timestamp: string;
  viralityScore: string;
  platformIcon: string;
  isOriginalSource: boolean;
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
  // Add properties as needed
}

export interface SearchInput {
  query?: string;
  images?: string[];
} 