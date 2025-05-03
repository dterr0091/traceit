export interface SearchResult {
  title: string;
  platform: string;
  timestamp: string;
  viralityScore: 'High' | 'Medium' | 'Low';
  platformIcon: string;
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