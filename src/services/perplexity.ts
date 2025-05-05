import axios from 'axios';
import { PerplexitySearchResponse, PerplexitySearchResult } from '../types/sourceTrace';

const PERPLEXITY_API_URL = 'https://api.perplexity.ai/sonar';
const PERPLEXITY_API_KEY = process.env.PERPLEXITY_API_KEY;

export class PerplexityService {
  async search(query: string, maxResults: number = 4): Promise<PerplexitySearchResult[]> {
    if (!PERPLEXITY_API_KEY) {
      throw new Error('PERPLEXITY_API_KEY environment variable is not set');
    }
    
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
} 