import 'dotenv/config';
import { SearchService } from './subframe-cursor-app/src/services/searchService.js';

async function testSearch() {
  const searchService = new SearchService();
  
  try {
    console.log('Testing search functionality...');
    
    // Test basic text search
    const { originalSources, viralPoints } = await searchService.search({
      text: 'climate change recent developments',
      max_results: 3
    });
    
    console.log('\nOriginal Sources:');
    originalSources.forEach((result, index) => {
      console.log(`\nSource ${index + 1}:`);
      console.log(`Title: ${result.title}`);
      console.log(`URL: ${result.url}`);
      console.log(`Published: ${result.timestamp}`);
      console.log(`Snippet: ${result.snippet?.substring(0, 150)}...`);
      
      if (result.engagement_metrics) {
        console.log('Engagement Metrics:');
        console.log(`  Views: ${result.engagement_metrics.views}`);
        console.log(`  Shares: ${result.engagement_metrics.shares}`);
        console.log(`  Comments: ${result.engagement_metrics.comments}`);
      }
    });

    console.log('\nViral Points:');
    viralPoints.forEach((result, index) => {
      console.log(`\nViral Point ${index + 1}:`);
      console.log(`Title: ${result.title}`);
      console.log(`URL: ${result.url}`);
      console.log(`Published: ${result.timestamp}`);
      console.log(`Snippet: ${result.snippet?.substring(0, 150)}...`);
      
      if (result.engagement_metrics) {
        console.log('Engagement Metrics:');
        console.log(`  Views: ${result.engagement_metrics.views}`);
        console.log(`  Shares: ${result.engagement_metrics.shares}`);
        console.log(`  Comments: ${result.engagement_metrics.comments}`);
      }
    });
    
  } catch (error) {
    console.error('Search test failed:');
    if (error instanceof Error) {
      console.error(`Error message: ${error.message}`);
      console.error(`Stack trace: ${error.stack}`);
    } else {
      console.error('Unknown error type:', error);
    }
  }
}

// Run the test and handle any uncaught errors
testSearch().catch(error => {
  console.error('Uncaught error in testSearch:');
  if (error instanceof Error) {
    console.error(`Error message: ${error.message}`);
    console.error(`Stack trace: ${error.stack}`);
  } else {
    console.error('Unknown error type:', error);
  }
  process.exit(1);
}); 