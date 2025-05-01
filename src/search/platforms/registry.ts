import { SearchInput } from '../types';
import { PlatformSearcher, PlatformSearchResult } from './types';
import { TwitterSearcher } from './twitter';

export class PlatformRegistry {
  private platforms: PlatformSearcher[] = [];

  constructor() {
    // Register default platforms
    this.registerPlatform(new TwitterSearcher());
    // TODO: Register other platforms (Facebook, Instagram, TikTok, etc.)
  }

  registerPlatform(platform: PlatformSearcher): void {
    this.platforms.push(platform);
  }

  async findPlatforms(input: SearchInput): Promise<PlatformSearcher[]> {
    const results = await Promise.all(
      this.platforms.map(async (platform) => ({
        platform,
        canHandle: await platform.canHandle(input)
      }))
    );

    return results
      .filter(result => result.canHandle)
      .map(result => result.platform);
  }

  async searchAcrossPlatforms(
    input: SearchInput,
    analysis: any
  ): Promise<PlatformSearchResult[]> {
    const platforms = await this.findPlatforms(input);
    
    const results = await Promise.all(
      platforms.map(platform => platform.search(input, analysis))
    );

    return results;
  }
} 