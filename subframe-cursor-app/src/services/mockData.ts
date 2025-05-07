import { SearchResult } from '../types/sourceTrace';

// Mock search results
export const mockSearchResults: SearchResult[] = [
  {
    title: "Original TechTrends Report: AI Impacts on Workforce Dynamics",
    platform: "TechCrunch",
    timestamp: "2024-03-15T10:30:00Z",
    viralityScore: "High",
    platformIcon: "news",
    isOriginalSource: true
  },
  {
    title: "Tech Companies Announce Major Layoffs Following AI Integration",
    platform: "LinkedIn",
    timestamp: "2024-03-15T14:15:00Z",
    viralityScore: "Medium",
    platformIcon: "linkedin",
    isOriginalSource: false
  },
  {
    title: "AI replacing jobs? Latest tech layoffs spark heated debate",
    platform: "Twitter",
    timestamp: "2024-03-15T16:45:00Z",
    viralityScore: "High",
    platformIcon: "twitter",
    isOriginalSource: false
  },
  {
    title: "r/technology discusses: Tech workforce reduction as AI adoption increases",
    platform: "Reddit",
    timestamp: "2024-03-16T07:30:00Z",
    viralityScore: "Medium",
    platformIcon: "reddit",
    isOriginalSource: false
  },
  {
    title: "Analysis: What the latest tech layoffs mean for the industry's future",
    platform: "Medium",
    timestamp: "2024-03-16T11:15:00Z",
    viralityScore: "Low",
    platformIcon: "medium",
    isOriginalSource: false
  },
  {
    title: "BREAKING: Major tech companies cut jobs as AI takes over key roles",
    platform: "Twitter",
    timestamp: "2024-03-16T13:30:00Z",
    viralityScore: "High",
    platformIcon: "twitter",
    isOriginalSource: false
  },
  {
    title: "Industry experts weigh in on AI-driven tech layoffs",
    platform: "YouTube",
    timestamp: "2024-03-17T09:45:00Z",
    viralityScore: "Medium",
    platformIcon: "youtube",
    isOriginalSource: false
  }
];

// Mock search by source topic - alternative dataset
export const mockPoliticalNews: SearchResult[] = [
  {
    title: "Breaking: New Policy Announcement from Administration",
    platform: "Washington Post",
    timestamp: "2024-03-10T08:30:00Z",
    viralityScore: "High",
    platformIcon: "news",
    isOriginalSource: true
  },
  {
    title: "Analysis: What the new policy means for voters",
    platform: "CNN",
    timestamp: "2024-03-10T10:15:00Z",
    viralityScore: "Medium",
    platformIcon: "news",
    isOriginalSource: false
  },
  {
    title: "Political experts react to controversial policy shift",
    platform: "Twitter",
    timestamp: "2024-03-10T12:45:00Z",
    viralityScore: "High",
    platformIcon: "twitter",
    isOriginalSource: false
  },
  {
    title: "r/politics megathread: Administration's new policy direction",
    platform: "Reddit",
    timestamp: "2024-03-10T14:20:00Z",
    viralityScore: "Medium",
    platformIcon: "reddit",
    isOriginalSource: false
  }
];

// Mock search for viral videos
export const mockViralVideo: SearchResult[] = [
  {
    title: "Amazing Skateboarding Trick Goes Wrong",
    platform: "TikTok",
    timestamp: "2024-02-28T16:30:00Z",
    viralityScore: "High",
    platformIcon: "tiktok",
    isOriginalSource: true
  },
  {
    title: "Compilation: Best Skateboarding Fails This Month",
    platform: "YouTube",
    timestamp: "2024-03-02T09:15:00Z",
    viralityScore: "Medium",
    platformIcon: "youtube",
    isOriginalSource: false
  },
  {
    title: "Skateboarding fail becomes internet sensation overnight",
    platform: "Instagram",
    timestamp: "2024-03-03T12:45:00Z",
    viralityScore: "High",
    platformIcon: "instagram",
    isOriginalSource: false
  },
  {
    title: "Skateboarder who went viral responds to internet fame",
    platform: "Twitter",
    timestamp: "2024-03-05T14:20:00Z",
    viralityScore: "Medium",
    platformIcon: "twitter",
    isOriginalSource: false
  }
];

// Mock change requests
export const mockCommunityNotes = [
  {
    id: 1,
    user: {
      name: 'John Doe',
      avatar: 'https://images.unsplash.com/photo-1599305445671-ac291c95aaa9',
      badge: 'Fact Checker'
    },
    content: 'Original source verified. The article contains direct quotes from the company CEO.',
    helpfulCount: 15,
    timestamp: '2024-03-15T10:30:00Z'
  },
  {
    id: 2,
    user: {
      name: 'Sarah Kim',
      avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330',
      badge: 'Expert'
    },
    content: 'I found an earlier reference to this on a different platform. The actual first appearance was on the company blog at 8:15 AM.',
    helpfulCount: 8,
    timestamp: '2024-03-15T11:45:00Z'
  },
  {
    id: 3,
    user: {
      name: 'Michael Chen',
      avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d',
      badge: 'Contributor'
    },
    content: 'The Twitter post contains additional context not present in the original article.',
    helpfulCount: 3,
    timestamp: '2024-03-15T14:20:00Z'
  }
];

// Mock API delay function
export const simulateApiDelay = (ms: number = 1000): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

// Mock search function - returns different results based on search terms
export const mockSearch = async (query: string): Promise<SearchResult[]> => {
  // Normalize the query for matching
  const normalizedQuery = query.toLowerCase();
  
  // Return different mock datasets based on query content
  if (normalizedQuery.includes('politic') || normalizedQuery.includes('policy') || normalizedQuery.includes('government')) {
    return mockPoliticalNews;
  } else if (normalizedQuery.includes('video') || normalizedQuery.includes('tiktok') || normalizedQuery.includes('viral')) {
    return mockViralVideo;
  } else {
    // Default to tech news for other queries
    return mockSearchResults;
  }
};

// Mock graph data generator to enrich limited search results
export const generateExtendedGraphData = (results: SearchResult[]): SearchResult[] => {
  if (!results || results.length === 0) {
    return [];
  }
  
  // If we already have enough results, return them as is
  if (results.length >= 5) {
    return results;
  }
  
  // Extract the original source
  const originalSource = results.find(r => r.isOriginalSource) || results[0];
  
  // Generate additional results based on the original
  const platforms = ['Twitter', 'LinkedIn', 'Reddit', 'Facebook', 'Instagram', 'YouTube', 'TikTok', 'Medium'];
  const viralityScores = ['High', 'Medium', 'Low'];
  
  // Create extended results
  const extendedResults: SearchResult[] = [...results];
  
  // Calculate how many additional results we need
  const additionalCount = 5 - results.length;
  
  for (let i = 0; i < additionalCount; i++) {
    // Add a random delay from the original for publication time
    const originalDate = new Date(originalSource.timestamp);
    const randomHours = Math.floor(Math.random() * 72) + 1; // 1-72 hours after original
    originalDate.setHours(originalDate.getHours() + randomHours);
    
    // Select platform that's not already in results
    let platform = platforms[Math.floor(Math.random() * platforms.length)];
    while (extendedResults.some(r => r.platform === platform)) {
      platform = platforms[Math.floor(Math.random() * platforms.length)];
    }
    
    // Create a derivative title
    const titles = [
      `${originalSource.title} - What You Need to Know`,
      `Breaking: ${originalSource.title.split(':')[1] || originalSource.title}`,
      `Analysis: Implications of ${originalSource.title.split(':')[1] || originalSource.title}`,
      `${platform} users react to "${originalSource.title.split(':')[1] || originalSource.title}"`,
      `${originalSource.title}: Industry experts weigh in`
    ];
    
    extendedResults.push({
      title: titles[Math.floor(Math.random() * titles.length)],
      platform: platform,
      timestamp: originalDate.toISOString(),
      viralityScore: viralityScores[Math.floor(Math.random() * viralityScores.length)],
      platformIcon: platform.toLowerCase(),
      isOriginalSource: false
    });
  }
  
  return extendedResults;
};

// Mock loading steps
export const mockLoadingSteps = [
  "Analyzing input...",
  "Searching web...",
  "Compiling results..."
]; 