from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl
import logging
from services.openai_service import OpenAIService
from services.api_integrations.perplexity import PerplexityAPI

logger = logging.getLogger(__name__)

class SearchResult(BaseModel):
    """Model representing a search result."""
    title: str
    url: HttpUrl
    platform: str
    timestamp: datetime
    virality_score: float = Field(ge=0, le=1)
    snippet: Optional[str] = None
    image_url: Optional[HttpUrl] = None

class SearchInput(BaseModel):
    """Model representing search input parameters."""
    text: str = ""
    image_urls: List[HttpUrl] = Field(default_factory=list)
    urls: List[HttpUrl] = Field(default_factory=list)
    max_results: int = Field(default=4, ge=1, le=10)

class SearchService:
    """Service for handling search functionality using Perplexity API."""
    
    def __init__(self):
        self.openai_service = OpenAIService()
        self.perplexity_api = PerplexityAPI()
        
    async def search(self, input_data: SearchInput) -> List[SearchResult]:
        """
        Perform a search using the Perplexity API.
        
        Args:
            input_data: SearchInput object containing search parameters
            
        Returns:
            List of SearchResult objects
            
        Raises:
            ValueError: If no valid search input is provided
        """
        if not input_data.text and not input_data.image_urls and not input_data.urls:
            raise ValueError("At least one of text, image_urls, or urls must be provided")
            
        try:
            # Use Perplexity API for web search
            search_results = await self.perplexity_api.search(
                query=input_data.text,
                image_urls=input_data.image_urls,
                urls=input_data.urls,
                max_results=input_data.max_results
            )
            
            # Process and validate results
            processed_results = []
            for result in search_results:
                try:
                    processed_result = SearchResult(
                        title=result.get("title", ""),
                        url=result.get("url"),
                        platform=result.get("platform", "Web"),
                        timestamp=datetime.fromisoformat(result.get("timestamp")),
                        virality_score=float(result.get("virality_score", 0)),
                        snippet=result.get("snippet"),
                        image_url=result.get("image_url")
                    )
                    processed_results.append(processed_result)
                except Exception as e:
                    logger.warning(f"Failed to process search result: {e}")
                    continue
                    
            return processed_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise 