import axios from 'axios';
import { PerplexitySearchResult, PerplexitySearchResponse, SearchInput } from '../types/sourceTrace';
import { OpenAIAnalysisService } from './openaiAnalysis';
import { getMockSearchResults } from './mockSearchData';

// Updated API URL to match latest Perplexity API
const PERPLEXITY_API_URL = 'https://api.perplexity.ai/chat/completions';
const PERPLEXITY_API_KEY = import.meta.env.VITE_PERPLEXITY_API_KEY;

// Flag to force using mock data even if API keys are present
const FORCE_MOCK_DATA = true; // Set to false in production

export class SearchService {
  private openaiAnalysis: OpenAIAnalysisService;
  private useMockData: boolean;

  constructor(useMockData: boolean = false) {
    this.openaiAnalysis = new OpenAIAnalysisService();
    this.useMockData = useMockData || FORCE_MOCK_DATA;
    
    // Log whether we're using mock data or real API
    if (this.useMockData) {
      console.log('SearchService: Using mock data for search results');
    }
  }

  private validateSearchResult(result: any): result is PerplexitySearchResult {
    return (
      typeof result === 'object' &&
      result !== null &&
      typeof result.title === 'string' &&
      typeof result.url === 'string' &&
      typeof result.snippet === 'string' &&
      typeof result.timestamp === 'string' &&
      typeof result.platform === 'string' &&
      typeof result.engagement_metrics === 'object' &&
      result.engagement_metrics !== null &&
      typeof result.engagement_metrics.views === 'number' &&
      typeof result.engagement_metrics.shares === 'number' &&
      typeof result.engagement_metrics.comments === 'number'
    );
  }

  private validateSearchResponse(response: any): response is PerplexitySearchResponse {
    return (
      typeof response === 'object' &&
      response !== null &&
      Array.isArray(response.results) &&
      response.results.every(this.validateSearchResult)
    );
  }

  private async callPerplexityAPI(query: string, maxResults: number = 4): Promise<PerplexitySearchResult[]> {
    // If mock data is enabled, return mock results instead of calling the API
    if (this.useMockData) {
      console.log('Using mock data instead of calling Perplexity API');
      // Simulate network latency
      await new Promise(resolve => setTimeout(resolve, 500));
      return getMockSearchResults(query, maxResults).originalSources.concat(
        getMockSearchResults(query, maxResults).viralPoints
      );
    }

    if (!PERPLEXITY_API_KEY) {
      console.error('Perplexity API key is missing. Please check your .env file and ensure VITE_PERPLEXITY_API_KEY is set.');
      console.log('Falling back to mock data');
      return getMockSearchResults(query, maxResults).originalSources.concat(
        getMockSearchResults(query, maxResults).viralPoints
      );
    }

    try {
      const response = await axios.post(
        PERPLEXITY_API_URL,
        {
          model: "sonar",
          messages: [
            {
              role: "system",
              content: "You are a helpful search assistant."
            },
            {
              role: "user",
              content: query
            }
          ],
          max_results: maxResults
        },
        {
          headers: {
            'Authorization': `Bearer ${PERPLEXITY_API_KEY}`,
            'Content-Type': 'application/json'
          },
          timeout: 10000 // 10 second timeout
        }
      );

      // Check if the response has the expected structure for the new API
      if (response.data && response.data.choices && response.data.choices[0]?.message?.tool_calls) {
        const searchResults = response.data.choices[0]?.message?.tool_calls[0]?.function?.arguments?.search_results || [];
        if (Array.isArray(searchResults)) {
          return searchResults;
        }
      }

      // If old API format
      if (this.validateSearchResponse(response.data)) {
        return response.data.results;
      }

      console.error('Invalid response format from Perplexity API:', response.data);
      console.log('Falling back to mock data');
      return getMockSearchResults(query, maxResults).originalSources.concat(
        getMockSearchResults(query, maxResults).viralPoints
      );
    } catch (error) {
      if (axios.isAxiosError(error)) {
        if (error.response) {
          // The request was made and the server responded with a status code
          // that falls out of the range of 2xx
          console.error('Perplexity API Error Response:', {
            status: error.response.status,
            data: error.response.data,
            headers: error.response.headers
          });
          
          console.log('API error, falling back to mock data');
        } else if (error.request) {
          // The request was made but no response was received
          console.error('No response received from Perplexity API:', error.request);
          console.log('Network error, falling back to mock data');
        } else {
          // Something happened in setting up the request that triggered an Error
          console.error('Error setting up Perplexity API request:', error.message);
          console.log('Setup error, falling back to mock data');
        }
      } else {
        // Non-Axios error
        console.error('Unexpected error calling Perplexity API:', error);
        console.log('Unexpected error, falling back to mock data');
      }
      
      // Fall back to mock data in all error cases
      return getMockSearchResults(query, maxResults).originalSources.concat(
        getMockSearchResults(query, maxResults).viralPoints
      );
    }
  }

  private getMockResults(query: string, maxResults: number): PerplexitySearchResult[] {
    // This basic mock function is kept for backward compatibility,
    // but we prefer using the more sophisticated mock data from mockSearchData.ts
    const now = new Date();
    return Array.from({ length: maxResults }, (_, i) => ({
      title: `Mock Result ${i + 1} for: ${query}`,
      url: `https://example.com/mock${i + 1}`,
      snippet: `This is a mock result for the query: ${query}`,
      timestamp: new Date(now.getTime() - i * 3600000).toISOString(),
      platform: ['Web', 'News', 'Blog', 'Social'][i % 4],
      engagement_metrics: {
        views: Math.floor(Math.random() * 10000),
        shares: Math.floor(Math.random() * 1000),
        comments: Math.floor(Math.random() * 500)
      }
    }));
  }

  private async analyzeWithOpenAI(results: PerplexitySearchResult[]): Promise<{
    originalSources: PerplexitySearchResult[];
    viralPoints: PerplexitySearchResult[];
  }> {
    try {
      // Skip OpenAI analysis if using mock data to avoid API costs
      if (this.useMockData) {
        console.log('Using mock analysis instead of OpenAI');
        const halfwayPoint = Math.ceil(results.length / 2);
        return {
          originalSources: results.slice(0, Math.min(3, halfwayPoint)),
          viralPoints: results.slice(halfwayPoint, halfwayPoint + Math.min(3, results.length - halfwayPoint))
        };
      }

      const analysis = await this.openaiAnalysis.analyzeContent({
        platform: 'web',
        title: results[0]?.title || '',
        content: results.map(r => r.snippet).join('\n'),
        plainText: results.map(r => r.snippet).join('\n'),
        date_published: results[0]?.timestamp || new Date().toISOString(),
        mediaUrls: [],
        url: results[0]?.url || ''
      });

      // Sort results by timestamp to find original sources
      const sortedResults = [...results].sort((a, b) => 
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
      );

      // Get up to 3 potential original sources
      const originalSources = sortedResults.slice(0, 3);

      // Get viral points for the first original source
      const viralPoints = results
        .filter(r => r.url !== originalSources[0]?.url)
        .sort((a, b) => {
          const aEngagement = (a.engagement_metrics?.views || 0) + 
                            (a.engagement_metrics?.shares || 0) + 
                            (a.engagement_metrics?.comments || 0);
          const bEngagement = (b.engagement_metrics?.views || 0) + 
                            (b.engagement_metrics?.shares || 0) + 
                            (b.engagement_metrics?.comments || 0);
          return bEngagement - aEngagement;
        })
        .slice(0, 3);

      return { originalSources, viralPoints };
    } catch (error) {
      console.error('Error in OpenAI analysis:', error);
      
      // Fall back to mock data if OpenAI analysis fails
      if (this.useMockData) {
        // If already using mock data, just divide the results
        const halfwayPoint = Math.ceil(results.length / 2);
        return {
          originalSources: results.slice(0, Math.min(3, halfwayPoint)),
          viralPoints: results.slice(halfwayPoint, halfwayPoint + Math.min(3, results.length - halfwayPoint))
        };
      } else {
        // If not already using mock data, use mock search results
        return getMockSearchResults(results[0]?.title || 'general search');
      }
    }
  }

  public async search(input: SearchInput): Promise<{
    originalSources: PerplexitySearchResult[];
    viralPoints: PerplexitySearchResult[];
  }> {
    const { text, image_urls, urls, max_results = 4 } = input;

    if (!text && (!image_urls || image_urls.length === 0) && (!urls || urls.length === 0)) {
      throw new Error('At least one of text, image_urls, or urls must be provided');
    }

    // If we're forcing mock data, just return mock results directly
    if (this.useMockData && text) {
      console.log('Directly returning mock search results');
      return getMockSearchResults(text, max_results);
    }

    // For now, we'll focus on text search. Image and URL search will be implemented later
    if (text) {
      try {
        const results = await this.callPerplexityAPI(text, max_results);
        return this.analyzeWithOpenAI(results);
      } catch (error) {
        console.error('Search failed, falling back to mock data:', error);
        return getMockSearchResults(text, max_results);
      }
    }

    // TODO: Implement image and URL search
    console.log('Image and URL search not implemented, using mock data');
    return getMockSearchResults("general search", max_results);
  }
} 