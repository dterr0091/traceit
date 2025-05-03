import { RedditExtractor } from './reddit';
import { YouTubeExtractor } from './youtube';
import { GenericArticleExtractor } from './genericArticle';
import { HeadlessExtractor } from './headless';
import { ExtractedPost, UnsupportedInputError } from '../types/ExtractedPost';

const EXTRACTORS = [
  RedditExtractor,
  YouTubeExtractor,
  GenericArticleExtractor,
  HeadlessExtractor
];

export async function extract(urlString: string): Promise<ExtractedPost> {
  let url: URL;
  try {
    url = new URL(urlString);
  } catch (error) {
    throw new UnsupportedInputError(`Invalid URL: ${urlString}`);
  }

  // Find the first extractor that can handle this URL
  for (const ExtractorClass of EXTRACTORS) {
    if (ExtractorClass.canHandle(url)) {
      const extractor = new ExtractorClass();
      try {
        return await extractor.extract(url);
      } catch (error) {
        // If this extractor fails, try the next one
        console.warn(`Extractor ${ExtractorClass.name} failed:`, error);
        continue;
      }
    }
  }

  throw new UnsupportedInputError(`No suitable extractor found for URL: ${urlString}`);
} 