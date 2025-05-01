import { z } from 'zod';
import OpenAI from 'openai';
import { VideoMetadata } from '../types/video';
import { logger } from '../utils/logger';
import { VideoProcessor } from './videoProcessor';
import { readFileSync } from 'fs';

const mediaAnalysisSchema = z.object({
  contentType: z.enum(['movie', 'tv_show', 'music', 'user_generated', 'other']),
  title: z.string(),
  source: z.object({
    name: z.string(),
    type: z.enum(['tv_show', 'movie', 'music_video', 'other']),
    episode: z.string().optional(),
    season: z.string().optional(),
    timestamp: z.string().optional(),
    releaseDate: z.string(),
  }),
  description: z.string(),
  confidence: z.number(),
});

type MediaAnalysisResult = z.infer<typeof mediaAnalysisSchema>;

export class MediaContentAnalyzer {
  private openai: OpenAI;
  private videoProcessor: VideoProcessor;
  
  constructor(apiKey: string) {
    this.openai = new OpenAI({ apiKey });
    this.videoProcessor = new VideoProcessor();
  }

  /**
   * Analyzes video content to identify its original source
   * @param videoUrl URL of the video to analyze
   * @param metadata Video metadata from the platform
   * @returns Promise<MediaAnalysisResult>
   */
  async analyzeVideoContent(
    videoUrl: string,
    metadata: VideoMetadata
  ): Promise<MediaAnalysisResult> {
    try {
      logger.info(`Analyzing video content for ${videoUrl}`);

      // Extract frames from video for analysis
      const framePaths = await this.videoProcessor.extractFrames(videoUrl);
      const frameBase64s = framePaths.map(path => {
        const buffer = readFileSync(path);
        return buffer.toString('base64');
      });
      
      // Analyze content using GPT-4 Vision
      const response = await this.openai.chat.completions.create({
        model: "gpt-4-vision-preview",
        messages: [
          {
            role: "system",
            content: `You are a media content identification expert. Analyze the provided video frames and return a JSON response with the following structure:
{
  "contentType": "movie|tv_show|music|user_generated|other",
  "title": "Full title of the content",
  "source": {
    "name": "Original source name",
    "type": "tv_show|movie|music_video|other",
    "episode": "Episode identifier (if applicable)",
    "season": "Season number (if applicable)",
    "timestamp": "Timestamp in the original content",
    "releaseDate": "Original release date (YYYY-MM-DD)"
  },
  "description": "Detailed description of the scene/content",
  "confidence": "Number between 0 and 1 indicating confidence in identification"
}

Consider the following when analyzing:
1. Look for distinctive visual elements, characters, or settings
2. Note any text overlays or captions
3. Consider the style and production quality
4. Look for any branding or watermarks
5. Use the video metadata for additional context

Be as specific and accurate as possible. If certain fields are not applicable or cannot be determined, omit them from the JSON response.

Video Metadata:
${JSON.stringify(metadata, null, 2)}`
          },
          {
            role: "user",
            content: [
              {
                type: "text",
                text: "Please identify the original source of this video content:"
              } as const,
              ...frameBase64s.map(base64 => ({
                type: "image_url" as const,
                image_url: {
                  url: `data:image/jpeg;base64,${base64}`
                }
              }))
            ]
          }
        ],
        max_tokens: 1000,
        response_format: { type: "json_object" }
      });

      // Parse and validate the response
      const content = response.choices[0]?.message?.content;
      if (!content) {
        throw new Error('No content in OpenAI response');
      }
      
      const analysis = this.parseAnalysisResponse(content);
      return mediaAnalysisSchema.parse(analysis);
    } catch (error) {
      logger.error('Error analyzing video content:', error);
      throw new Error('Failed to analyze video content');
    }
  }

  /**
   * Parses the GPT-4 Vision response into structured data
   * @param response Raw response from GPT-4 Vision
   * @returns Structured analysis result
   */
  private parseAnalysisResponse(response: string): MediaAnalysisResult {
    try {
      // Parse the JSON response from GPT-4 Vision
      const parsedResponse = JSON.parse(response);

      // Map the response to our schema
      const result: MediaAnalysisResult = {
        contentType: this.validateEnum(parsedResponse.contentType, [
          'movie', 'tv_show', 'music', 'user_generated', 'other'
        ]) as MediaAnalysisResult['contentType'],
        title: parsedResponse.title || 'Unknown Title',
        source: {
          name: parsedResponse.source?.name || 'Unknown Source',
          type: this.validateEnum(parsedResponse.source?.type, [
            'tv_show', 'movie', 'music_video', 'other'
          ]) as MediaAnalysisResult['source']['type'],
          ...(parsedResponse.source?.episode && { episode: parsedResponse.source.episode }),
          ...(parsedResponse.source?.season && { season: parsedResponse.source.season }),
          ...(parsedResponse.source?.timestamp && { timestamp: parsedResponse.source.timestamp }),
          releaseDate: parsedResponse.source?.releaseDate || '1970-01-01',
        },
        description: parsedResponse.description || 'No description available',
        confidence: this.validateConfidence(parsedResponse.confidence),
      };

      return result;
    } catch (error) {
      logger.error('Error parsing analysis response:', error);
      throw new Error('Failed to parse analysis response');
    }
  }

  /**
   * Validates that a value is one of the allowed enum values
   * @param value The value to validate
   * @param allowedValues Array of allowed values
   * @returns The validated value or a default value
   */
  private validateEnum(value: any, allowedValues: string[]): string {
    return allowedValues.includes(value) ? value : allowedValues[allowedValues.length - 1];
  }

  /**
   * Validates and normalizes a confidence score
   * @param value The confidence score to validate
   * @returns A number between 0 and 1
   */
  private validateConfidence(value: any): number {
    const num = Number(value);
    if (isNaN(num)) return 0.5;
    return Math.max(0, Math.min(1, num));
  }
} 