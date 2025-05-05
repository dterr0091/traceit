import OpenAI from 'openai';
import { ExtractedPost } from '../types';

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

export class OpenAIAnalysisService {
  private openai: OpenAI | null;

  constructor() {
    const apiKey = import.meta.env.VITE_OPENAI_API_KEY;
    if (!apiKey) {
      console.warn('OpenAI API key not found. Some features may be limited.');
      this.openai = null;
    } else {
      this.openai = new OpenAI({
        apiKey: apiKey,
        dangerouslyAllowBrowser: true
      });
    }
  }

  public async analyzeContent(post: ExtractedPost): Promise<AnalysisResult> {
    // If OpenAI is not available, return mock data
    if (!this.openai) {
      return {
        searchQueries: [
          `${post.title} original source`,
          `${post.title} first appearance`,
          `${post.title} earliest mention`
        ],
        keyTopics: post.title.split(' ').slice(0, 3),
        suggestedTimeframe: '2020-2024'
      };
    }

    try {
      const response = await this.openai.chat.completions.create({
        model: 'gpt-4-turbo-preview',
        messages: [
          {
            role: 'system',
            content: 'You are an expert content analyst. Analyze the provided content and generate search queries to find the original source and related content. Focus on identifying key topics and suggesting a relevant timeframe for the search.'
          },
          {
            role: 'user',
            content: this.buildTextPrompt(post)
          }
        ],
        temperature: 0.7,
        max_tokens: 1000
      });

      const content = response.choices[0]?.message?.content;
      if (!content) {
        throw new Error('Empty response from OpenAI');
      }

      try {
        const result = JSON.parse(content) as AnalysisResult;
        this.validateAnalysisResult(result);
        return result;
      } catch (error) {
        throw new Error('Invalid OpenAI response format');
      }
    } catch (error) {
      console.error('Error in OpenAI analysis:', error);
      // Return mock data if OpenAI fails
      return {
        searchQueries: [
          `${post.title} original source`,
          `${post.title} first appearance`,
          `${post.title} earliest mention`
        ],
        keyTopics: post.title.split(' ').slice(0, 3),
        suggestedTimeframe: '2020-2024'
      };
    }
  }

  private buildTextPrompt(post: ExtractedPost): string {
    return `
      Analyze the following content and generate search queries to find its original source and related content:

      Title: ${post.title}
      Content: ${post.content}
      Publication Date: ${post.date_published}
      Platform: ${post.platform}

      Please provide:
      1. Three search queries optimized for finding the original source and related content
      2. Key topics identified in the content
      3. A suggested timeframe for the search (e.g., "2020-2023")

      Format your response as a JSON object with the following structure:
      {
        "searchQueries": ["query1", "query2", "query3"],
        "keyTopics": ["topic1", "topic2"],
        "suggestedTimeframe": "YYYY-YYYY"
      }
    `;
  }

  private validateAnalysisResult(result: AnalysisResult): void {
    if (!result.searchQueries || !Array.isArray(result.searchQueries) || result.searchQueries.length === 0) {
      throw new Error('Invalid search queries in analysis result');
    }
    if (!result.keyTopics || !Array.isArray(result.keyTopics) || result.keyTopics.length === 0) {
      throw new Error('Invalid key topics in analysis result');
    }
    if (!result.suggestedTimeframe || typeof result.suggestedTimeframe !== 'string') {
      throw new Error('Invalid suggested timeframe in analysis result');
    }
  }
} 