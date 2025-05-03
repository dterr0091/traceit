// Simple test script to verify dotenv loading
require('dotenv').config();

console.log('Testing dotenv loading:');
console.log('OPENAI_API_KEY:', process.env.OPENAI_API_KEY ? 'defined' : 'undefined');
console.log('SONAR_API_KEY:', process.env.SONAR_API_KEY ? 'defined' : 'undefined'); 