import axios from 'axios';
import { Extractor } from './base';
import { ExtractedPost } from '../types/ExtractedPost';

interface RedditPost {
  data: {
    children: Array<{
      data: {
        title: string;
        author: string;
        selftext: string;
        created_utc: number;
        url: string;
        is_video: boolean;
        media?: {
          reddit_video?: {
            fallback_url: string;
          };
        };
        preview?: {
          images: Array<{
            source: {
              url: string;
            };
          }>;
        };
      };
    }>;
  };
}

export class RedditExtractor extends Extractor {
  static canHandle(url: URL): boolean {
    return url.hostname === 'reddit.com' || url.hostname === 'www.reddit.com';
  }

  async extract(url: URL): Promise<ExtractedPost> {
    this.validateUrl(url);

    // Extract post ID from URL
    const matches = url.pathname.match(/\/comments\/([a-zA-Z0-9]+)/);
    if (!matches) {
      throw new Error('Invalid Reddit URL format');
    }

    const postId = matches[1];
    const response = await axios.get<[RedditPost]>(
      `https://www.reddit.com/comments/${postId}.json`,
      {
        headers: {
          'User-Agent': 'Traceit/1.0.0'
        }
      }
    );

    const post = response.data[0].data.children[0].data;

    const mediaUrls: string[] = [];
    if (post.is_video && post.media?.reddit_video) {
      mediaUrls.push(post.media.reddit_video.fallback_url);
    } else if (post.preview?.images) {
      mediaUrls.push(post.preview.images[0].source.url);
    }

    return {
      platform: 'reddit',
      url: url.href,
      author: post.author,
      timestamp: new Date(post.created_utc * 1000),
      title: post.title,
      plainText: post.selftext || post.title,
      mediaUrls: mediaUrls.length > 0 ? mediaUrls : undefined
    };
  }
} 