import axios from 'axios';
import { PerplexitySearchResult, PerplexitySearchResponse, SearchInput } from '../types/sourceTrace';
import { OpenAIAnalysisService } from './openaiAnalysis';

const PERPLEXITY_API_URL = 'https://api.perplexity.ai/sonar';
const PERPLEXITY_API_KEY = import.meta.env.PERPLEXITY_API_KEY;

export class SearchService {
  private openaiAnalysis: OpenAIAnalysisService;

  constructor() {
    this.openaiAnalysis = new OpenAIAnalysisService();
  }

  private async callPerplexityAPI(query: string, maxResults: number = 4): Promise<PerplexitySearchResult[]> {
    if (!PERPLEXITY_API_KEY) {
      console.warn('Perplexity API key not found. Using mock data.');
      return this.getMockResults(query, maxResults);
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
      return this.getMockResults(query, maxResults);
    }
  }

  private getMockResults(query: string, maxResults: number): PerplexitySearchResult[] {
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
      // Return mock data if analysis fails
      return {
        originalSources: results.slice(0, 3),
        viralPoints: results.slice(3, 6)
      };
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

    // For now, we'll focus on text search. Image and URL search will be implemented later
    if (text) {
      const results = await this.callPerplexityAPI(text, max_results);
      return this.analyzeWithOpenAI(results);
    }

    // TODO: Implement image and URL search
    throw new Error('Image and URL search not yet implemented');
  }
} 