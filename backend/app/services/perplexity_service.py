import httpx
import os
import json
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from .redis_service import redis_service

load_dotenv()

PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_API_URL = "https://api.perplexity.ai/sonar/search"

class PerplexityService:
    def __init__(self):
        self.api_key = PERPLEXITY_API_KEY
        self.api_url = PERPLEXITY_API_URL
        
    async def search(self, query: str, cache_key: Optional[str] = None) -> Dict[str, Any]:
        """
        Search using Perplexity API with caching
        
        Args:
            query: Search query
            cache_key: Optional cache key (defaults to query hash)
            
        Returns:
            Search results
        """
        # Use provided cache key or query as key
        cache_key = cache_key or f"perplexity:{query}"
        
        # Check cache first
        cached_result = redis_service.get_cache(cache_key)
        if cached_result:
            return cached_result
            
        # Not in cache, call API
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "max_results": 4,  # Limit results to control costs
            "include_citations": True,
            "include_sources": True
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30.0  # Longer timeout for complex queries
            )
            
            response.raise_for_status()
            result = response.json()
            
            # Cache the result (30 day TTL)
            redis_service.set_cache(cache_key, result, ttl_days=30)
            
            return result
            
# Initialize singleton
perplexity_service = PerplexityService() 