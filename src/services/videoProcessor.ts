import { spawn } from 'child_process';
import { createWriteStream, mkdirSync, existsSync } from 'fs';
import { join } from 'path';
import { pipeline } from 'stream/promises';
import fetch from 'node-fetch';
import { logger } from '../utils/logger';

export class VideoProcessor {
  private readonly outputDir: string;
  private readonly maxFrames: number;

  constructor(outputDir: string = 'tmp/frames', maxFrames: number = 5) {
    this.outputDir = outputDir;
    this.maxFrames = maxFrames;
    this.ensureOutputDir();
  }

  /**
   * Downloads a video from a URL and extracts key frames
   * @param videoUrl The URL of the video to process
   * @returns Promise<string[]> Array of paths to extracted frames
   */
  async extractFrames(videoUrl: string): Promise<string[]> {
    try {
      // Create a unique directory for this video's frames
      const videoId = this.getVideoId(videoUrl);
      const videoDir = join(this.outputDir, videoId);
      this.ensureOutputDir(videoDir);

      // Download the video
      const videoPath = join(videoDir, 'video.mp4');
      await this.downloadVideo(videoUrl, videoPath);

      // Extract frames using ffmpeg
      const framePattern = join(videoDir, 'frame-%d.jpg');
      await this.extractKeyFrames(videoPath, framePattern);

      // Get the paths of extracted frames
      const framePaths: string[] = [];
      for (let i = 1; i <= this.maxFrames; i++) {
        const framePath = join(videoDir, `frame-${i}.jpg`);
        if (existsSync(framePath)) {
          framePaths.push(framePath);
        }
      }

      return framePaths;
    } catch (error) {
      logger.error('Error processing video:', error);
      throw new Error('Failed to process video');
    }
  }

  /**
   * Downloads a video from a URL to a local file
   * @param url The URL of the video
   * @param outputPath The path to save the video to
   */
  private async downloadVideo(url: string, outputPath: string): Promise<void> {
    try {
      const response = await fetch(url);
      if (!response.ok) {
        throw new Error(`Failed to fetch video: ${response.statusText}`);
      }

      const fileStream = createWriteStream(outputPath);
      if (!response.body) {
        throw new Error('No response body');
      }

      await pipeline(response.body, fileStream);
    } catch (error) {
      logger.error('Error downloading video:', error);
      throw new Error('Failed to download video');
    }
  }

  /**
   * Extracts key frames from a video using ffmpeg
   * @param videoPath Path to the input video
   * @param outputPattern Pattern for output frame filenames
   */
  private async extractKeyFrames(videoPath: string, outputPattern: string): Promise<void> {
    return new Promise((resolve, reject) => {
      // Use ffmpeg to extract frames at regular intervals
      const ffmpeg = spawn('ffmpeg', [
        '-i', videoPath,
        '-vf', `select='eq(pict_type,PICT_TYPE_I)'`, // Extract I-frames only
        '-vsync', 'vfr',
        '-frames:v', this.maxFrames.toString(),
        '-y', // Overwrite existing files
        outputPattern
      ]);

      ffmpeg.stderr.on('data', (data) => {
        logger.debug(`ffmpeg: ${data}`);
      });

      ffmpeg.on('close', (code) => {
        if (code === 0) {
          resolve();
        } else {
          reject(new Error(`ffmpeg exited with code ${code}`));
        }
      });

      ffmpeg.on('error', (err) => {
        reject(err);
      });
    });
  }

  /**
   * Ensures the output directory exists
   * @param dir Optional specific directory to create
   */
  private ensureOutputDir(dir?: string): void {
    const targetDir = dir || this.outputDir;
    if (!existsSync(targetDir)) {
      mkdirSync(targetDir, { recursive: true });
    }
  }

  /**
   * Extracts a unique identifier from a video URL
   * @param url The video URL
   * @returns A unique identifier for the video
   */
  private getVideoId(url: string): string {
    try {
      const urlObj = new URL(url);
      if (urlObj.hostname.includes('youtube.com')) {
        if (urlObj.pathname.startsWith('/shorts/')) {
          return urlObj.pathname.split('/')[2];
        }
        return urlObj.searchParams.get('v') || 'unknown';
      }
      // For other platforms, use the last path segment
      const segments = urlObj.pathname.split('/').filter(Boolean);
      return segments[segments.length - 1];
    } catch {
      return Date.now().toString();
    }
  }
} 