// Use CommonJS format
const dotenv = require('dotenv');

// Load environment variables from .env file
dotenv.config();

console.log('Testing environment variable loading:');
console.log('OPENAI_API_KEY available:', !!process.env.OPENAI_API_KEY);
console.log('SONAR_API_KEY available:', !!process.env.SONAR_API_KEY);

// Print all environment variables (redacted for security)
console.log('\nAll environment variables (redacted):');
Object.keys(process.env).forEach(key => {
  if (key.includes('KEY') || key.includes('SECRET') || key.includes('TOKEN')) {
    console.log(`${key}: [REDACTED]`);
  } else {
    console.log(`${key}: ${process.env[key]}`);
  }
}); 