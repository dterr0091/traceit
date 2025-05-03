// Import dotenv to load environment variables
import 'dotenv/config';

const OPENAI_API_KEY = process.env.OPENAI_API_KEY;
const SONAR_API_KEY = process.env.SONAR_API_KEY;

// Function to mask API keys for display
function maskApiKey(key) {
  if (!key) return 'Not available';
  if (key.length <= 10) return '****'; // Too short to meaningfully mask
  return key.substring(0, 4) + '...' + key.substring(key.length - 4);
}

// Check API keys
console.log('API Key Check:');
console.log('==============');
console.log(`OPENAI_API_KEY: ${OPENAI_API_KEY ? 'Available' : 'Not available'} (${maskApiKey(OPENAI_API_KEY)})`);
console.log(`OPENAI_API_KEY length: ${OPENAI_API_KEY ? OPENAI_API_KEY.length : 'N/A'}`);
console.log(`OPENAI_API_KEY format: ${OPENAI_API_KEY?.startsWith('sk-') ? 'Valid format (starts with sk-)' : 'Invalid format'}`);
console.log('');
console.log(`SONAR_API_KEY: ${SONAR_API_KEY ? 'Available' : 'Not available'} (${maskApiKey(SONAR_API_KEY)})`);
console.log(`SONAR_API_KEY length: ${SONAR_API_KEY ? SONAR_API_KEY.length : 'N/A'}`);
console.log(`SONAR_API_KEY format: ${SONAR_API_KEY?.startsWith('pplx-') ? 'Valid format (starts with pplx-)' : 'Possibly invalid format'}`);

console.log('\nEnvironment Information:');
console.log('=======================');
// Show Node.js version
console.log(`Node.js version: ${process.version}`);
// Show OS info
console.log(`OS: ${process.platform} ${process.arch}`); 