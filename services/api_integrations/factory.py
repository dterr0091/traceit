from typing import Dict, Type
from .base import BaseAPIIntegration
from .reddit import RedditIntegration
from .twitter import TwitterIntegration
from .instagram import InstagramIntegration
from .youtube import YouTubeIntegration
from .news import NewsIntegration

class APIIntegrationFactory:
    """Factory class for creating API integration instances."""
    
    _integrations: Dict[str, Type[BaseAPIIntegration]] = {
        'reddit': RedditIntegration,
        'twitter': TwitterIntegration,
        'instagram': InstagramIntegration,
        'youtube': YouTubeIntegration,
        'news': NewsIntegration
    }
    
    @classmethod
    def create_integration(cls, platform: str, **kwargs) -> BaseAPIIntegration:
        """Create an API integration instance for the specified platform.
        
        Args:
            platform: Platform name ('reddit', 'twitter', 'instagram', 'youtube', 'news')
            **kwargs: Platform-specific initialization parameters
            
        Returns:
            API integration instance
            
        Raises:
            ValueError: If the platform is not supported
        """
        integration_class = cls._integrations.get(platform.lower())
        if not integration_class:
            raise ValueError(f"Unsupported platform: {platform}")
        
        return integration_class(**kwargs)
    
    @classmethod
    def get_supported_platforms(cls) -> list:
        """Get list of supported platforms.
        
        Returns:
            List of supported platform names
        """
        return list(cls._integrations.keys())
    
    @classmethod
    def get_required_credentials(cls, platform: str) -> list:
        """Get required credentials for a platform.
        
        Args:
            platform: Platform name
            
        Returns:
            List of required credential names
            
        Raises:
            ValueError: If the platform is not supported
        """
        integration_class = cls._integrations.get(platform.lower())
        if not integration_class:
            raise ValueError(f"Unsupported platform: {platform}")
        
        # Get the __init__ method's parameters
        init_params = integration_class.__init__.__annotations__
        return [param for param in init_params if param != 'return'] 