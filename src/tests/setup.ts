import dotenv from 'dotenv';

// Load environment variables from .env.test file
dotenv.config({ path: '.env.test' });

// Mock OpenAI API key for testing
process.env.OPENAI_API_KEY = 'test-api-key';

// Add any other test setup here 