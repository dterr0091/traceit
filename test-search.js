// Import dotenv to load environment variables
import 'dotenv/config';

const PERPLEXITY_API_URL = 'https://api.perplexity.ai/chat/completions';
const PERPLEXITY_API_KEY = process.env.SONAR_API_KEY; // Use the environment variable

async function callPerplexityAPI(query, maxResults = 3) {
  try {
    console.log(`Using API key: ${PERPLEXITY_API_KEY ? 'Available' : 'Not available'}`);
    
    const response = await fetch(PERPLEXITY_API_URL, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${PERPLEXITY_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: "sonar",
        messages: [
          {
            role: "system",
            content: "You are a helpful search assistant."
          },
          {
            role: "user",
            content: query
          }
        ],
        max_results: maxResults,
      })
    });

    if (!response.ok) {
      throw new Error(`API request failed with status ${response.status}: ${await response.text()}`);
    }
    
    const data = await response.json();
    console.log('Full API response:', JSON.stringify(data, null, 2));
    
    // Extract search results from the response
    const searchResults = data.choices && data.choices[0]?.message?.tool_calls?.[0]?.function?.arguments?.search_results || [];
    
    return searchResults;
  } catch (error) {
    console.error('Error calling Perplexity API:', error.message);
    throw new Error('Failed to perform search');
  }
}

async function testSearch() {
  try {
    console.log('Testing search functionality...');
    console.log('Environment variables loaded:', process.env.OPENAI_API_KEY ? 'Yes' : 'No');
    console.log('SONAR_API_KEY available:', !!process.env.SONAR_API_KEY);
    
    // Test basic text search
    const results = await callPerplexityAPI('climate change recent developments', 3);
    
    console.log(`Found ${results.length} results:`);
    results.forEach((result, index) => {
      console.log(`\nResult ${index + 1}:`);
      console.log(`Title: ${result.title}`);
      console.log(`URL: ${result.url}`);
      console.log(`Published Date: ${result.published_date || 'Not available'}`);
      console.log(`Snippet: ${result.snippet?.substring(0, 150)}...`);
      
      if (result.engagement_metrics) {
        console.log('Engagement Metrics:');
        console.log(`  Views: ${result.engagement_metrics.views || 'N/A'}`);
        console.log(`  Shares: ${result.engagement_metrics.shares || 'N/A'}`);
        console.log(`  Comments: ${result.engagement_metrics.comments || 'N/A'}`);
      }
    });
    
  } catch (error) {
    console.error('Search test failed:', error);
  }
}

testSearch().catch(console.error); 