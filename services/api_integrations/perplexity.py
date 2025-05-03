from typing import List, Optional, Dict, Any
from datetime import datetime
import logging
import httpx
from pydantic import HttpUrl
from config import settings

logger = logging.getLogger(__name__)

class PerplexityAPI:
    """Real implementation of Perplexity API."""
    
    def __init__(self):
        """Initialize the Perplexity API client."""
        self.api_url = "https://api.perplexity.ai/sonar"
        self.api_key = settings.PERPLEXITY_API_KEY
        
    async def search(
        self,
        query: str = "",
        image_urls: List[HttpUrl] = None,
        urls: List[HttpUrl] = None,
        max_results: int = 4
    ) -> List[Dict[str, Any]]:
        """
        Perform a search using the Perplexity API.
        
        Args:
            query: Search query text
            image_urls: List of image URLs to search
            urls: List of URLs to analyze
            max_results: Maximum number of results to return
            
        Returns:
            List of search results
        """
        if image_urls is None:
            image_urls = []
        if urls is None:
            urls = []
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.api_url,
                    json={
                        "query": query,
                        "max_results": max_results,
                        "include_engagement_metrics": True
                    },
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    timeout=30.0
                )
                
                response.raise_for_status()
                data = response.json()
                
                # Transform results to match our expected format
                results = []
                for result in data.get("results", []):
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("url"),
                        "platform": "Web",  # Perplexity is web search
                        "timestamp": datetime.utcnow().isoformat(),  # Use current time as Perplexity doesn't provide timestamps
                        "virality_score": self._calculate_virality_score(result),
                        "snippet": result.get("snippet"),
                        "image_url": result.get("image_url")
                    })
                    
                return results
                
        except Exception as e:
            logger.error(f"Perplexity API search failed: {e}")
            raise
            
    def _calculate_virality_score(self, result: Dict[str, Any]) -> float:
        """Calculate a virality score from engagement metrics."""
        metrics = result.get("engagement_metrics", {})
        if not metrics:
            return 0.0
            
        # Normalize engagement metrics to a 0-1 scale
        views = metrics.get("views", 0)
        shares = metrics.get("shares", 0)
        comments = metrics.get("comments", 0)
        
        # Simple scoring formula - can be adjusted based on needs
        total = views + (shares * 10) + (comments * 5)  # Weight shares and comments more heavily
        return min(1.0, total / 10000)  # Cap at 1.0 