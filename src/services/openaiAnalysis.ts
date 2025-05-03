import OpenAI from 'openai';
import { ExtractedPost, AnalysisResult } from '../types';
import axios from 'axios';

export class OpenAIAnalysisService {
  private openai: OpenAI;

  constructor() {
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY,
    });
  }

  async analyzeContent(post: ExtractedPost): Promise<AnalysisResult> {
    try {
      if (post.mediaUrls.length > 0) {
        return await this.analyzeWithVision(post);
      } else {
        return await this.analyzeTextOnly(post);
      }
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to analyze content with OpenAI: ${error.message}`);
      }
      throw new Error('Failed to analyze content with OpenAI');
    }
  }

  private async analyzeWithVision(post: ExtractedPost): Promise<AnalysisResult> {
    const imageUrl = post.mediaUrls[0];
    
    // Download the image to get its base64 representation
    const imageResponse = await axios.get(imageUrl, { responseType: 'arraybuffer' });
    const base64Image = Buffer.from(imageResponse.data).toString('base64');

    const response = await this.openai.chat.completions.create({
      model: 'gpt-4-vision-preview',
      messages: [
        {
          role: 'system',
          content: 'You are an expert content analyst. Analyze the provided content and image to generate search queries for finding the original source and related content. Focus on identifying key topics, visual elements, and suggesting a relevant timeframe for the search.'
        },
        {
          role: 'user',
          content: [
            {
              type: 'text',
              text: this.buildVisionPrompt(post)
            },
            {
              type: 'image_url',
              image_url: {
                url: `data:image/jpeg;base64,${base64Image}`
              }
            }
          ]
        }
      ],
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
  }

  private async analyzeTextOnly(post: ExtractedPost): Promise<AnalysisResult> {
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
  }

  private buildVisionPrompt(post: ExtractedPost): string {
    return `
      Analyze the following content and image to generate search queries for finding the original source and related content:

      Title: ${post.title}
      Author: ${post.author}
      Publication Date: ${post.date_published}
      Content: ${post.content}

      Please provide:
      1. Three search queries optimized for finding the original source and related content
      2. Key topics identified in the content
      3. A suggested timeframe for the search (e.g., "2020-2023")
      4. Image analysis including:
         - A detailed description of the image
         - Key objects/people/places identified
         - Any text visible in the image

      Format your response as a JSON object with the following structure:
      {
        "searchQueries": ["query1", "query2", "query3"],
        "keyTopics": ["topic1", "topic2"],
        "suggestedTimeframe": "YYYY-YYYY",
        "imageAnalysis": {
          "description": "detailed description",
          "objects": ["object1", "object2"],
          "text": ["text1", "text2"]
        }
      }
    `;
  }

  private buildTextPrompt(post: ExtractedPost): string {
    return `
      Analyze the following content and generate search queries to find its original source and related content:

      Title: ${post.title}
      Author: ${post.author}
      Publication Date: ${post.date_published}
      Content: ${post.content}

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
    if (!Array.isArray(result.searchQueries) || result.searchQueries.length === 0) {
      throw new Error('Invalid search queries in analysis result');
    }
    if (!Array.isArray(result.keyTopics) || result.keyTopics.length === 0) {
      throw new Error('Invalid key topics in analysis result');
    }
    if (typeof result.suggestedTimeframe !== 'string' || !result.suggestedTimeframe) {
      throw new Error('Invalid suggested timeframe in analysis result');
    }
    if (result.imageAnalysis) {
      if (typeof result.imageAnalysis.description !== 'string' || !result.imageAnalysis.description) {
        throw new Error('Invalid image description in analysis result');
      }
      if (!Array.isArray(result.imageAnalysis.objects)) {
        throw new Error('Invalid image objects in analysis result');
      }
      if (!Array.isArray(result.imageAnalysis.text)) {
        throw new Error('Invalid image text in analysis result');
      }
    }
  }
} 