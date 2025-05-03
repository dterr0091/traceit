import 'dotenv/config';
import { SearchService } from './subframe-cursor-app/src/services/searchService.js';

async function testSearch() {
  try {
    console.log('Creating SearchService instance...');
    const searchService = new SearchService();
    
    console.log('Testing search functionality...');
    
    // Test basic text search
    console.log('Calling search method...');
    const searchResult = await searchService.search({
      text: 'climate change recent developments',
      max_results: 3
    });
    
    console.log('Search result:', JSON.stringify(searchResult, null, 2));
    
    const { originalSources, viralPoints } = searchResult;
    
    console.log('\nOriginal Sources:');
    if (originalSources && originalSources.length > 0) {
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
    } else {
      console.log('No original sources found');
    }

    console.log('\nViral Points:');
    if (viralPoints && viralPoints.length > 0) {
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
    } else {
      console.log('No viral points found');
    }
    
  } catch (error) {
    console.error('Search test failed:');
    if (error instanceof Error) {
      console.error(`Error message: ${error.message}`);
      console.error(`Stack trace: ${error.stack}`);
    } else {
      console.error('Unknown error type:', JSON.stringify(error, null, 2));
    }
  }
}

// Run the test and handle any uncaught errors
testSearch().catch(error => {
  console.error('Uncaught error in testSearch:');
  console.error(error);
  process.exit(1);
}); 