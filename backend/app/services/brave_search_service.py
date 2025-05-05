import os
import requests
import logging
from typing import Dict, Any, Optional, List
from ..utils.bloom_filter import BloomFilter

logger = logging.getLogger(__name__)

class BraveSearchService:
    """Service for interacting with Brave Search API for reverse image search"""
    
    BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")
    BRAVE_API_URL = "https://api.search.brave.com/res/v1/images/search/reverse"
    
    @staticmethod
    async def reverse_image_search(image_data: bytes) -> Dict[str, Any]:
        """
        Perform reverse image search using Brave Search API
        
        Args:
            image_data: Binary image data
            
        Returns:
            Dict containing search results from Brave Search
        """
        if not BraveSearchService.BRAVE_API_KEY:
            raise ValueError("BRAVE_API_KEY environment variable not set")
        
        headers = {
            "X-Subscription-Token": BraveSearchService.BRAVE_API_KEY,
            "Accept": "application/json"
        }
        
        files = {
            "image": image_data
        }
        
        try:
            response = requests.post(
                BraveSearchService.BRAVE_API_URL,
                headers=headers,
                files=files
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error calling Brave Search API: {str(e)}")
            return {"error": str(e), "results": []}
    
    @staticmethod
    def extract_origins(brave_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract origin information from Brave Search results
        
        Args:
            brave_results: Raw results from Brave Search API
            
        Returns:
            List of origin objects with normalized structure
        """
        origins = []
        
        if "results" not in brave_results or not brave_results["results"]:
            return origins
        
        for result in brave_results["results"]:
            try:
                # Extract relevant information from Brave result
                origin = {
                    "url": result.get("url", ""),
                    "title": result.get("title", ""),
                    "source": "brave_search",
                    "timestamp": result.get("published", ""),  # May need to normalize date format
                    "similarity": result.get("similarity", 0.0) if "similarity" in result else 0.0,
                    "confidence": min(result.get("confidence", 0.0) if "confidence" in result else 0.0, 1.0),
                    "metadata": {
                        "domain": result.get("domain", ""),
                        "width": result.get("width", 0),
                        "height": result.get("height", 0),
                        "alt_text": result.get("alt", "")
                    }
                }
                origins.append(origin)
            except Exception as e:
                logger.error(f"Error processing Brave result: {str(e)}")
                continue
        
        # Sort by confidence or similarity
        origins.sort(key=lambda x: (x["confidence"], x["similarity"]), reverse=True)
        
        return origins[:10]  # Limit to top 10 results 