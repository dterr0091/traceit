import { SearchResult, SearchState } from '../types/sourceTrace';

export class SearchService {
  private apiUrl = process.env.VITE_API_URL ?? 'http://localhost:3000/api';

  async search(query: string): Promise<SearchResult[]> {
    try {
      const response = await fetch(`${this.apiUrl}/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          post: {
            title: query,
            content: query,
            date_published: new Date().toISOString(),
            platform: 'web'
          }
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      
      // Transform the response into SearchResult format
      return [{
        title: data.title || query,
        platform: data.platform || 'web',
        timestamp: new Date().toISOString(),
        viralityScore: 'High',
        platformIcon: 'web',
        isOriginalSource: true
      }];
    } catch (error) {
      console.error('Search error:', error);
      throw new Error('An error occurred during the search. Please try again.');
    }
  }

  async analyzeResults(results: SearchResult[]): Promise<SearchState> {
    return {
      isLoading: false,
      currentStep: '',
      error: null,
      results: results
    };
  }
} 