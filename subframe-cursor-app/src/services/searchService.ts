import axios from 'axios';
import { PerplexitySearchResult, PerplexitySearchResponse, SearchInput } from '../types/sourceTrace';

const PERPLEXITY_API_URL = 'https://api.perplexity.ai/sonar';
const PERPLEXITY_API_KEY = import.meta.env.PERPLEXITY_API_KEY;

export class SearchService {
  private async callPerplexityAPI(query: string, maxResults: number = 4): Promise<PerplexitySearchResult[]> {
    try {
      const response = await axios.post<PerplexitySearchResponse>(
        PERPLEXITY_API_URL,
        {
          query,
          max_results: maxResults,
          include_engagement_metrics: true
        },
        {
          headers: {
            'Authorization': `Bearer ${PERPLEXITY_API_KEY}`,
            'Content-Type': 'application/json'
          }
        }
      );

      return response.data.results;
    } catch (error) {
      console.error('Error calling Perplexity API:', error);
      throw new Error('Failed to perform search');
    }
  }

  public async search(input: SearchInput): Promise<PerplexitySearchResult[]> {
    const { text, image_urls, urls, max_results = 4 } = input;

    if (!text && (!image_urls || image_urls.length === 0) && (!urls || urls.length === 0)) {
      throw new Error('At least one of text, image_urls, or urls must be provided');
    }

    // For now, we'll focus on text search. Image and URL search will be implemented later
    if (text) {
      return this.callPerplexityAPI(text, max_results);
    }

    // TODO: Implement image and URL search
    throw new Error('Image and URL search not yet implemented');
  }
} 