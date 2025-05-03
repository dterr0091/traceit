export interface PerplexitySearchResult {
  url: string;
  title: string;
  snippet: string;
  published_date?: string;
  engagement_metrics?: {
    views?: number;
    shares?: number;
    comments?: number;
  };
}

export interface PerplexitySearchResponse {
  results: PerplexitySearchResult[];
}

export interface SearchInput {
  text?: string;
  image_urls?: string[];
  urls?: string[];
  max_results?: number;
} 