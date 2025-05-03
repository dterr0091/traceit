import { Extractor } from './base';
import { RedditExtractor } from './reddit';
import { YouTubeExtractor } from './youtube';
import { MercuryArticleExtractor } from './mercuryArticle';
import { HeadlessFallbackExtractor } from './headlessFallback';
import { GenericArticleExtractor } from './genericArticle';
import { HeadlessExtractor } from './headless';
import { ExtractedPost } from '../types';
import { UnsupportedInputError } from '../types/ExtractedPost';

// Define the list of extractor classes, not instances
const EXTRACTOR_CLASSES = [
  RedditExtractor,
  YouTubeExtractor,
  MercuryArticleExtractor,
  HeadlessFallbackExtractor,
  GenericArticleExtractor,
  HeadlessExtractor,
];

export async function extract(urlString: string): Promise<ExtractedPost> {
  let urlObj: URL;
  try {
    urlObj = new URL(urlString);
  } catch (error) {
    throw new UnsupportedInputError(`Invalid URL: ${urlString}`);
  }

  // Find the first eligible extractor class
  for (const ExtractorClass of EXTRACTOR_CLASSES) {
    // Instantiate the class to check eligibility
    const extractorInstance = new ExtractorClass();
    if (await extractorInstance.isEligible(urlString)) {
      try {
        // Use the instance to extract
        return await extractorInstance.extract(urlString);
      } catch (error) {
        // If this extractor fails, log and try the next one
        console.warn(`Extractor ${ExtractorClass.name} failed for ${urlString}:`, error);
        continue;
      }
    }
  }

  throw new UnsupportedInputError(`No suitable extractor found for URL: ${urlString}`);
} 