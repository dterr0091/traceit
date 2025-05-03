from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from datetime import datetime
import logging
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class BaseAPIIntegration(ABC):
    """Base class for all API integrations."""
    
    def __init__(self, api_key: Optional[str] = None, api_secret: Optional[str] = None):
        """Initialize the API integration with credentials.
        
        Args:
            api_key: API key for authentication
            api_secret: API secret for authentication
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self._client = None
    
    @property
    @abstractmethod
    def client(self) -> Any:
        """Get the API client instance."""
        pass
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    @abstractmethod
    async def search_content(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Search for content across the platform.
        
        Args:
            query: Search query string
            **kwargs: Additional search parameters
            
        Returns:
            List of content items matching the search criteria
        """
        pass
    
    @abstractmethod
    async def get_content_details(self, content_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific content item.
        
        Args:
            content_id: Unique identifier for the content
            
        Returns:
            Detailed information about the content
        """
        pass
    
    @abstractmethod
    async def get_user_content(self, username: str, **kwargs) -> List[Dict[str, Any]]:
        """Get content posted by a specific user.
        
        Args:
            username: Username of the content creator
            **kwargs: Additional parameters for filtering
            
        Returns:
            List of content items posted by the user
        """
        pass
    
    def _format_timestamp(self, timestamp: Any) -> str:
        """Format timestamp to ISO format.
        
        Args:
            timestamp: Timestamp to format
            
        Returns:
            ISO formatted timestamp string
        """
        if isinstance(timestamp, (int, float)):
            return datetime.fromtimestamp(timestamp).isoformat()
        elif isinstance(timestamp, str):
            return timestamp
        elif isinstance(timestamp, datetime):
            return timestamp.isoformat()
        else:
            raise ValueError(f"Unsupported timestamp type: {type(timestamp)}")
    
    def _log_error(self, error: Exception, context: str):
        """Log error with context.
        
        Args:
            error: Exception that occurred
            context: Context in which the error occurred
        """
        logger.error(f"Error in {context}: {str(error)}", exc_info=True) 