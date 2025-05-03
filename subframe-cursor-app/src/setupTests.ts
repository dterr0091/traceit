import '@testing-library/jest-dom'; 

// Set up test environment variables
process.env.VITE_API_URL = 'http://localhost:3000/api';
process.env.VITE_AUTH0_DOMAIN = 'test.auth0.com';
process.env.VITE_AUTH0_CLIENT_ID = 'test-client-id';
process.env.VITE_PERPLEXITY_API_KEY = 'test-perplexity-key';
process.env.VITE_OPENAI_API_KEY = 'test-openai-key'; 