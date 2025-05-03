import { SearchResult, SearchState } from '../types/sourceTrace';

// Mock platform icons (replace with actual icons later)
const PLATFORM_ICONS = {
  twitter: 'https://images.unsplash.com/photo-1611162617474-5b21e879e113',
  reddit: 'https://images.unsplash.com/photo-1611162616305-c69b3fa7fbe0',
  instagram: 'https://images.unsplash.com/photo-1611162618071-b39a2ec055fb',
  youtube: 'https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7',
  news: 'https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7'
};

// Mock search results
export const mockSearchResults: SearchResult[] = [
  {
    title: "Tech Workforce Reduction",
    platform: "Twitter",
    timestamp: "March 15, 9:00 AM",
    viralityScore: "High",
    platformIcon: PLATFORM_ICONS.twitter
  },
  {
    title: "AI Impact on Tech Jobs",
    platform: "Reddit",
    timestamp: "March 15, 10:30 AM",
    viralityScore: "Medium",
    platformIcon: PLATFORM_ICONS.reddit
  },
  {
    title: "Industry Workforce Trends",
    platform: "Instagram",
    timestamp: "March 15, 2:15 PM",
    viralityScore: "Low",
    platformIcon: PLATFORM_ICONS.instagram
  },
  {
    title: "Tech Layoffs Analysis",
    platform: "YouTube",
    timestamp: "March 15, 4:45 PM",
    viralityScore: "High",
    platformIcon: PLATFORM_ICONS.youtube
  },
  {
    title: "Tech Industry Report",
    platform: "News",
    timestamp: "March 15, 6:30 PM",
    viralityScore: "Medium",
    platformIcon: PLATFORM_ICONS.news
  }
];

// Mock community notes
export const mockCommunityNotes = [
  {
    id: 1,
    user: {
      name: "John Smith",
      avatar: "https://images.unsplash.com/photo-1535713875002-d1d0cf377fde",
      badge: "Fact Checker"
    },
    content: "Original source verified through archived timestamps and digital signatures. Content appears to be authentic based on multiple verification methods.",
    helpfulCount: 24,
    timestamp: "March 15, 8:30 PM"
  },
  {
    id: 2,
    user: {
      name: "Alice Chen",
      avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330",
      badge: "Researcher"
    },
    content: "Additional context: Similar claims appeared in private forums 24 hours before the viral spread, but couldn't be independently verified.",
    helpfulCount: 18,
    timestamp: "March 15, 9:15 PM"
  }
];

// Mock API delay function
export const simulateApiDelay = (ms: number = 1000): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

// Mock search function
export const mockSearch = async (query: string, images: string[]): Promise<SearchResult[]> => {
  await simulateApiDelay(2000);
  
  // Filter results based on query if provided
  if (query) {
    const filteredResults = mockSearchResults.filter(result => 
      result.title.toLowerCase().includes(query.toLowerCase()) ||
      result.platform.toLowerCase().includes(query.toLowerCase())
    );
    
    // If no results match the query, return all results
    return filteredResults.length > 0 ? filteredResults : mockSearchResults;
  }
  
  return mockSearchResults;
};

// Mock loading steps
export const mockLoadingSteps = [
  "Analyzing input...",
  "Searching web...",
  "Compiling results..."
]; 