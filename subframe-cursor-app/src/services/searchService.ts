import { SearchResult, SearchState } from '../types/sourceTrace';
import { mockSearchResults } from './mockData';

export class SearchService {
  async search(query: string): Promise<SearchResult[]> {
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Return mock results
      return mockSearchResults;
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