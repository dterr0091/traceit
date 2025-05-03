// Import dotenv to load environment variables
import 'dotenv/config';

// Mock search result data
const MOCK_SEARCH_RESULTS = {
  originalSources: [
    {
      title: "Latest Climate Change Report Shows Alarming Trends",
      url: "https://example.com/climate-report-2024",
      timestamp: "2024-05-01T12:30:45Z",
      snippet: "According to the newest IPCC report, global temperatures have risen faster in the past decade than previously predicted. Climate scientists warn that immediate action is required to prevent catastrophic effects on ecosystems and human populations worldwide.",
      platform: ["News", "Scientific"],
      engagement_metrics: {
        views: 125000,
        shares: 45000,
        comments: 8700
      }
    },
    {
      title: "New Technologies Addressing Climate Change",
      url: "https://example.com/climate-tech-innovations",
      timestamp: "2024-04-27T09:15:20Z",
      snippet: "Breakthrough carbon capture technologies are showing promising results in pilot programs across Europe and North America. These innovations could potentially remove billions of tons of CO2 from the atmosphere annually if deployed at scale.",
      platform: ["Technology", "Science"],
      engagement_metrics: {
        views: 89000,
        shares: 28000,
        comments: 5200
      }
    },
    {
      title: "International Climate Summit Announces New Agreements",
      url: "https://example.com/climate-summit-2024",
      timestamp: "2024-04-15T18:45:10Z",
      snippet: "Representatives from 195 countries have signed a new agreement to accelerate the transition to renewable energy. The landmark deal includes firm commitments to phase out coal power by 2035 and increase climate financing for developing nations.",
      platform: ["Politics", "News"],
      engagement_metrics: {
        views: 215000,
        shares: 76000,
        comments: 12500
      }
    }
  ],
  viralPoints: [
    {
      title: "Climate Activists Block Major Highway in Protest",
      url: "https://example.com/climate-protests-highway",
      timestamp: "2024-05-02T10:20:30Z",
      snippet: "Environmental activists brought traffic to a standstill on a major interstate today as part of a coordinated climate action. The protesters demanded immediate government action on climate change and fossil fuel subsidies.",
      platform: ["Social", "News"],
      engagement_metrics: {
        views: 430000,
        shares: 185000,
        comments: 32800
      }
    },
    {
      title: "Celebrity's Viral Climate Speech Reaches Millions",
      url: "https://example.com/celebrity-climate-speech",
      timestamp: "2024-04-29T14:25:50Z",
      snippet: "A Hollywood actor's impassioned speech about climate change has gone viral on social media, amassing over 50 million views in just 48 hours. The celebrity called for systemic change and corporate accountability.",
      platform: ["Social", "Entertainment"],
      engagement_metrics: {
        views: 1250000,
        shares: 780000,
        comments: 92500
      }
    },
    {
      title: "Dramatic Glacier Collapse Footage Shocks Viewers",
      url: "https://example.com/glacier-collapse-footage",
      timestamp: "2024-04-18T08:10:15Z",
      snippet: "Time-lapse footage showing the rapid collapse of Antarctica's Pine Island Glacier has shocked viewers worldwide. Scientists note that the ice shelf has lost an area roughly the size of Chicago in just the past month.",
      platform: ["Science", "Video"],
      engagement_metrics: {
        views: 875000,
        shares: 390000,
        comments: 45600
      }
    }
  ]
};

// Mock search function
async function mockSearch(query, maxResults = 4) {
  console.log(`[MOCK] Searching for: "${query}" with max results: ${maxResults}`);
  
  // Simulate API latency
  await new Promise(resolve => setTimeout(resolve, 800));
  
  // Return limited results based on maxResults parameter
  return {
    originalSources: MOCK_SEARCH_RESULTS.originalSources.slice(0, maxResults),
    viralPoints: MOCK_SEARCH_RESULTS.viralPoints.slice(0, maxResults)
  };
}

async function testSearch() {
  try {
    console.log('Testing MOCK search functionality...');
    console.log('No API keys needed - using mock data');
    
    // Test basic text search
    console.log('Calling mock search method...');
    const { originalSources, viralPoints } = await mockSearch('climate change recent developments', 3);
    
    console.log('\nOriginal Sources:');
    if (originalSources && originalSources.length > 0) {
      originalSources.forEach((result, index) => {
        console.log(`\nSource ${index + 1}:`);
        console.log(`Title: ${result.title}`);
        console.log(`URL: ${result.url}`);
        console.log(`Published: ${result.timestamp}`);
        console.log(`Snippet: ${result.snippet.substring(0, 150)}...`);
        
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
        console.log(`Snippet: ${result.snippet.substring(0, 150)}...`);
        
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

// Run the mock test
testSearch().catch(error => {
  console.error('Uncaught error in testSearch:');
  console.error(error);
  process.exit(1);
}); 