import { exec } from 'child_process';
import { promisify } from 'util';
import { existsSync } from 'fs';
import { join } from 'path';
import chromium from '@sparticuz/chromium';

const execAsync = promisify(exec);

async function downloadChromium() {
  const chromiumPath = process.env.CHROMIUM_EXECUTABLE_PATH || 
    join(process.cwd(), 'node_modules/@sparticuz/chromium/bin/chromium');

  if (existsSync(chromiumPath)) {
    console.log('Chromium already exists at:', chromiumPath);
    return;
  }

  console.log('Attempting to download Chromium...');
  try {
    const executablePath = await chromium.executablePath();
    console.log('Chromium downloaded successfully to:', executablePath);
  } catch (error) {
    console.warn('Could not download Chromium. Some features may be limited:', error);
    // Don't exit with error, just continue
  }
}

downloadChromium().catch(error => {
  console.warn('Chromium download failed, continuing without it:', error);
}); 