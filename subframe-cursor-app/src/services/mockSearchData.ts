import { PerplexitySearchResult } from '../types/sourceTrace';

// Enhanced mock search result data with realistic information
export const MOCK_SEARCH_RESULTS: Record<string, {
  originalSources: PerplexitySearchResult[],
  viralPoints: PerplexitySearchResult[]
}> = {
  // Default/fallback results for any query
  default: {
    originalSources: [
      {
        title: "Latest Climate Change Report Shows Alarming Trends",
        url: "https://example.com/climate-report-2024",
        timestamp: "2024-05-01T12:30:45Z",
        snippet: "According to the newest IPCC report, global temperatures have risen faster in the past decade than previously predicted. Climate scientists warn that immediate action is required to prevent catastrophic effects on ecosystems and human populations worldwide.",
        platform: "News",
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
        platform: "Technology",
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
        platform: "Politics",
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
        platform: "Social",
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
        platform: "Entertainment",
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
        platform: "Science",
        engagement_metrics: {
          views: 875000,
          shares: 390000,
          comments: 45600
        }
      }
    ]
  },
  
  // Results for technology or AI-related queries
  technology: {
    originalSources: [
      {
        title: "New AI Breakthrough Challenges Previous Limitations",
        url: "https://example.com/ai-breakthrough-2024",
        timestamp: "2024-05-02T14:25:10Z",
        snippet: "Researchers at a leading AI lab have announced a breakthrough in large language model architecture that significantly reduces computational requirements while improving performance. The new approach could make advanced AI more accessible.",
        platform: "Technology",
        engagement_metrics: {
          views: 95000,
          shares: 35000,
          comments: 6800
        }
      },
      {
        title: "Tech Giants Announce Collaboration on AI Safety Standards",
        url: "https://example.com/ai-safety-standards",
        timestamp: "2024-04-28T08:15:30Z",
        snippet: "Major technology companies have formed an unprecedented coalition to establish industry-wide safety standards for artificial intelligence deployment. The initiative follows growing concerns about unregulated AI development.",
        platform: "Business",
        engagement_metrics: {
          views: 120000,
          shares: 42000,
          comments: 7500
        }
      },
      {
        title: "The Evolution of Quantum Computing: New Milestones",
        url: "https://example.com/quantum-computing-milestones",
        timestamp: "2024-04-20T11:35:40Z",
        snippet: "Quantum computing reached several significant milestones this quarter, with researchers demonstrating practical quantum advantage in materials science applications. These advances could accelerate development of new pharmaceutical compounds and energy storage solutions.",
        platform: "Science",
        engagement_metrics: {
          views: 78000,
          shares: 22000,
          comments: 4100
        }
      }
    ],
    viralPoints: [
      {
        title: "AI-Generated Art Wins Controversial International Prize",
        url: "https://example.com/ai-art-prize-controversy",
        timestamp: "2024-05-03T09:10:25Z",
        snippet: "An AI-generated artwork has won a prestigious international art competition, sparking intense debate about the nature of creativity and authorship. The artist used a custom-trained AI model but claims the work represents genuine artistic expression.",
        platform: "Arts",
        engagement_metrics: {
          views: 540000,
          shares: 285000,
          comments: 42800
        }
      },
      {
        title: "Tech CEO's Viral Prediction About AI Revolution Goes Viral",
        url: "https://example.com/ceo-ai-prediction",
        timestamp: "2024-04-30T16:20:15Z",
        snippet: "A controversial prediction about AI replacing 80% of knowledge work within five years has gone viral after being shared by a prominent tech CEO. The statement has sparked both criticism and support from industry experts.",
        platform: "Business",
        engagement_metrics: {
          views: 950000,
          shares: 520000,
          comments: 65500
        }
      },
      {
        title: "Smartphone's Revolutionary Feature Demonstration Wows Online",
        url: "https://example.com/smartphone-feature-demo",
        timestamp: "2024-04-22T13:40:35Z",
        snippet: "A demonstration video of a next-generation smartphone feature has garnered millions of views. The technology appears to enable real-time language translation through augmented reality glasses connected to the phone.",
        platform: "Technology",
        engagement_metrics: {
          views: 1875000,
          shares: 790000,
          comments: 115600
        }
      }
    ]
  }
};

// Helper function to get mock data for a specific query
export function getMockSearchResults(query: string, maxResults: number = 4): {
  originalSources: PerplexitySearchResult[];
  viralPoints: PerplexitySearchResult[];
} {
  // Check if query contains tech-related keywords
  const techKeywords = ['ai', 'artificial intelligence', 'tech', 'technology', 'computer', 'software', 'hardware', 'programming', 'digital', 'innovation'];
  
  // Determine which dataset to use based on the query
  const datasetKey = techKeywords.some(keyword => query.toLowerCase().includes(keyword)) 
    ? 'technology' 
    : 'default';
  
  // Get the appropriate dataset
  const mockData = MOCK_SEARCH_RESULTS[datasetKey];
  
  // Return limited results based on maxResults parameter
  return {
    originalSources: mockData.originalSources.slice(0, maxResults),
    viralPoints: mockData.viralPoints.slice(0, maxResults)
  };
} 