// Simple manual implementation to read .env file
const fs = require('fs');
const path = require('path');

function loadEnv() {
  try {
    const envPath = path.resolve(process.cwd(), '.env');
    console.log(`Looking for .env file at: ${envPath}`);
    
    if (fs.existsSync(envPath)) {
      console.log('.env file exists!');
      const envContent = fs.readFileSync(envPath, 'utf8');
      
      // Parse the content
      const envVars = envContent.split('\n').reduce((acc, line) => {
        // Skip empty lines and comments
        if (!line || line.startsWith('#')) return acc;
        
        // Parse key=value
        const match = line.match(/^([^=]+)=(.*)$/);
        if (match) {
          const key = match[1].trim();
          const value = match[2].trim();
          acc[key] = value;
          
          // Also set in process.env
          process.env[key] = value;
        }
        
        return acc;
      }, {});
      
      console.log('Parsed environment variables:');
      Object.keys(envVars).forEach(key => {
        if (key.includes('KEY') || key.includes('SECRET') || key.includes('TOKEN')) {
          console.log(`${key}: [REDACTED]`);
        } else {
          console.log(`${key}: ${envVars[key]}`);
        }
      });
      
      return envVars;
    } else {
      console.log('.env file not found');
      return {};
    }
  } catch (error) {
    console.error('Error loading .env file:', error);
    return {};
  }
}

// Load the environment variables
const envVars = loadEnv();

// Check specific keys
console.log('\nVerifying specific keys:');
console.log('OPENAI_API_KEY available:', !!envVars.OPENAI_API_KEY);
console.log('SONAR_API_KEY available:', !!envVars.SONAR_API_KEY);

// Now these variables should be available in process.env as well
console.log('\nVerifying process.env:');
console.log('OPENAI_API_KEY in process.env:', !!process.env.OPENAI_API_KEY);
console.log('SONAR_API_KEY in process.env:', !!process.env.SONAR_API_KEY); 