import { Extractor } from './base';
import { RedditExtractor } from './reddit';
import { YouTubeExtractor } from './youtube';
import { MercuryArticleExtractor } from './mercuryArticle';
import { HeadlessFallbackExtractor } from './headlessFallback';
import { GenericArticleExtractor } from './genericArticle';
import { HeadlessExtractor } from './headless';
import { ExtractedPost, UnsupportedInputError } from '../types/ExtractedPost';

export const EXTRACTORS: Extractor[] = [
  new RedditExtractor(),
  new YouTubeExtractor(),
  new MercuryArticleExtractor(),
  new HeadlessFallbackExtractor()
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
      const extractor = ExtractorClass;
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