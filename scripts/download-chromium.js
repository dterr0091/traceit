import { exec } from 'child_process';
import { promisify } from 'util';
import { existsSync } from 'fs';
import { join } from 'path';
import chrome from 'chrome-aws-lambda';

const execAsync = promisify(exec);

async function downloadChromium() {
  const chromiumPath = process.env.CHROMIUM_EXECUTABLE_PATH || 
    join(process.cwd(), 'chromium', 'chrome');

  if (existsSync(chromiumPath)) {
    console.log('Chromium already exists at:', chromiumPath);
    return;
  }

  console.log('Downloading Chromium...');
  try {
    const { executablePath } = await chrome.executablePath;
    console.log('Chromium downloaded successfully to:', executablePath);
  } catch (error) {
    console.error('Failed to download Chromium:', error);
    process.exit(1);
  }
}

downloadChromium().catch(console.error); 