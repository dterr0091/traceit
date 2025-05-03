import { config } from 'dotenv';
import { resolve } from 'path';

// Load test environment variables
config({ path: resolve(process.cwd(), '.env.test') });

// Set default environment variables for tests
process.env.YTDLP_BINARY = process.env.YTDLP_BINARY || '/usr/local/bin/yt-dlp';
process.env.CHROMIUM_PATH = process.env.CHROMIUM_PATH || '/opt/chromium/chrome'; 