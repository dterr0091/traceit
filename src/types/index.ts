export interface ExtractedPost {
  platform: string;
  title: string;
  author: string;
  date_published: string;
  content: string;
  plainText: string;
  mediaUrls: string[];
  url: string;
}

export interface Extractor {
  isEligible(url: string): Promise<boolean>;
  extract(url: string): Promise<ExtractedPost>;
}

export interface AnalysisResult {
  searchQueries: string[];
  keyTopics: string[];
  suggestedTimeframe: string;
  imageAnalysis?: {
    description: string;
    objects: string[];
    text: string[];
  };
} 