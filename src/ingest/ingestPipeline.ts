import { extract } from '../extractors/router';
import { ExtractedPost, UnsupportedInputError } from '../types/ExtractedPost';

interface IngestInput {
  url?: string;
  filePath?: string;
}

// Placeholder for future video/image processing
async function processMediaFile(filePath: string): Promise<ExtractedPost> {
  // TODO: Implement video/image processing pipeline:
  // 1. Use ffmpeg to extract frames/audio
  // 2. Use Whisper for audio transcription
  // 3. Use OpenAI Vision for image analysis
  throw new Error('Media file processing not implemented yet');
}

export async function ingest(input: IngestInput): Promise<ExtractedPost> {
  if (!input.url && !input.filePath) {
    throw new UnsupportedInputError('Either url or filePath must be provided');
  }

  let result: ExtractedPost;

  if (input.filePath) {
    result = await processMediaFile(input.filePath);
  } else if (input.url) {
    result = await extract(input.url);
  } else {
    throw new UnsupportedInputError('Invalid input');
  }

  // TODO: After extraction, trigger Perplexity Sonar search loop:
  // 1. Extract key terms from result.plainText
  // 2. Search for similar content across platforms
  // 3. Analyze temporal relationships
  // 4. Build content propagation graph

  return result;
} 