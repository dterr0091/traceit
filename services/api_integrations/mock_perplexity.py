from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import HttpUrl

class MockPerplexityAPI:
    """Mock implementation of Perplexity API for testing."""
    
    def search(
        self,
        query: str = "",
        image_urls: List[HttpUrl] = None,
        urls: List[HttpUrl] = None,
        max_results: int = 4
    ) -> List[dict]:
        """
        Mock search implementation that returns sample data.
        
        Args:
            query: Search query text
            image_urls: List of image URLs to search
            urls: List of URLs to analyze
            max_results: Maximum number of results to return
            
        Returns:
            List of mock search results
        """
        if image_urls is None:
            image_urls = []
        if urls is None:
            urls = []
            
        # Generate mock results based on input type
        results = []
        base_time = datetime.now()
        
        if query:
            results.extend([
                {
                    "title": f"Result for query: {query}",
                    "url": "https://example.com/result1",
                    "platform": "Web",
                    "timestamp": (base_time - timedelta(hours=1)).isoformat(),
                    "virality_score": 0.8,
                    "snippet": f"This is a sample result for the query: {query}",
                    "image_url": "https://example.com/image1.jpg"
                },
                {
                    "title": f"Another result for: {query}",
                    "url": "https://example.com/result2",
                    "platform": "News",
                    "timestamp": (base_time - timedelta(hours=2)).isoformat(),
                    "virality_score": 0.6,
                    "snippet": f"Additional information about {query}",
                    "image_url": "https://example.com/image2.jpg"
                }
            ])
            
        if image_urls:
            results.extend([
                {
                    "title": "Image Analysis Result",
                    "url": "https://example.com/image-analysis",
                    "platform": "Image Search",
                    "timestamp": base_time.isoformat(),
                    "virality_score": 0.7,
                    "snippet": "This image appears to be related to the search query",
                    "image_url": str(image_urls[0])
                }
            ])
            
        if urls:
            results.extend([
                {
                    "title": "URL Analysis Result",
                    "url": str(urls[0]),
                    "platform": "URL Analysis",
                    "timestamp": (base_time - timedelta(minutes=30)).isoformat(),
                    "virality_score": 0.9,
                    "snippet": "Analysis of the provided URL",
                    "image_url": "https://example.com/url-analysis.jpg"
                }
            ])
            
        return results[:max_results] 