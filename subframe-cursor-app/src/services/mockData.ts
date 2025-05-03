import { SearchResult } from '../types/sourceTrace';

// Mock search results
export const mockSearchResults: SearchResult[] = [
  {
    title: "Breaking News: Major Tech Company Announcement",
    platform: "Twitter",
    timestamp: "2024-03-15T10:30:00Z",
    viralityScore: "High",
    platformIcon: "twitter",
    isOriginalSource: true
  },
  {
    title: "Tech Industry Analysis",
    platform: "LinkedIn",
    timestamp: "2024-03-15T09:15:00Z",
    viralityScore: "Medium",
    platformIcon: "linkedin",
    isOriginalSource: false
  },
  {
    title: "Tech News Roundup",
    platform: "Reddit",
    timestamp: "2024-03-15T08:45:00Z",
    viralityScore: "Low",
    platformIcon: "reddit",
    isOriginalSource: false
  },
  {
    title: "Industry Expert Commentary",
    platform: "Twitter",
    timestamp: "2024-03-15T07:30:00Z",
    viralityScore: "High",
    platformIcon: "twitter",
    isOriginalSource: false
  },
  {
    title: "Tech Community Discussion",
    platform: "LinkedIn",
    timestamp: "2024-03-15T06:15:00Z",
    viralityScore: "Medium",
    platformIcon: "linkedin",
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
      badge: 'Expert'
    },
    content: 'This appears to be the original source.',
    helpfulCount: 15,
    timestamp: '2024-03-15T10:30:00Z'
  }
];

// Mock API delay function
export const simulateApiDelay = (ms: number = 1000): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

// Mock search function
export const mockSearch = async (): Promise<SearchResult[]> => {
  return [
    {
      title: 'Original Post',
      platform: 'Twitter',
      timestamp: new Date().toISOString(),
      viralityScore: 'High',
      platformIcon: 'twitter',
      isOriginalSource: true
    }
  ];
};

// Mock loading steps
export const mockLoadingSteps = [
  "Analyzing input...",
  "Searching web...",
  "Compiling results..."
]; 