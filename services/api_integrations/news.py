from typing import Any, Dict, List, Optional
from newsapi import NewsApiClient
from .base import BaseAPIIntegration

class NewsIntegration(BaseAPIIntegration):
    """News API integration."""
    
    def __init__(self, api_key: str):
        """Initialize News API integration.
        
        Args:
            api_key: News API key
        """
        super().__init__(api_key, None)
        self._client = None
    
    @property
    def client(self) -> NewsApiClient:
        """Get the News API client instance."""
        if self._client is None:
            self._client = NewsApiClient(api_key=self.api_key)
        return self._client
    
    async def search_content(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Search for news articles.
        
        Args:
            query: Search query string
            **kwargs: Additional search parameters
                - language: Language code (default: 'en')
                - sort_by: Sort method ('relevancy', 'popularity', 'publishedAt')
                - from_date: Start date (ISO 8601 format)
                - to_date: End date (ISO 8601 format)
                - page_size: Number of results per page (default: 10)
                - page: Page number (default: 1)
                
        Returns:
            List of news articles matching the search criteria
        """
        try:
            language = kwargs.get('language', 'en')
            sort_by = kwargs.get('sort_by', 'relevancy')
            from_date = kwargs.get('from_date')
            to_date = kwargs.get('to_date')
            page_size = kwargs.get('page_size', 10)
            page = kwargs.get('page', 1)
            
            response = self.client.get_everything(
                q=query,
                language=language,
                sort_by=sort_by,
                from_param=from_date,
                to=to_date,
                page_size=page_size,
                page=page
            )
            
            return [self._format_article(article) for article in response['articles']]
        except Exception as e:
            self._log_error(e, "News search_content")
            return []
    
    async def get_content_details(self, url: str) -> Dict[str, Any]:
        """Get detailed information about a news article.
        
        Args:
            url: Article URL
            
        Returns:
            Detailed information about the article
        """
        try:
            # News API doesn't provide a direct way to get article by URL
            # We'll search for the URL and return the first match
            response = self.client.get_everything(
                q=url,
                language='en',
                sort_by='relevancy',
                page_size=1
            )
            
            if response['articles']:
                return self._format_article(response['articles'][0])
            return {}
        except Exception as e:
            self._log_error(e, "News get_content_details")
            return {}
    
    async def get_user_content(self, source: str, **kwargs) -> List[Dict[str, Any]]:
        """Get articles from a specific news source.
        
        Args:
            source: News source ID
            **kwargs: Additional parameters
                - language: Language code (default: 'en')
                - page_size: Number of results per page (default: 10)
                - page: Page number (default: 1)
                
        Returns:
            List of articles from the source
        """
        try:
            language = kwargs.get('language', 'en')
            page_size = kwargs.get('page_size', 10)
            page = kwargs.get('page', 1)
            
            response = self.client.get_top_headlines(
                sources=source,
                language=language,
                page_size=page_size,
                page=page
            )
            
            return [self._format_article(article) for article in response['articles']]
        except Exception as e:
            self._log_error(e, "News get_user_content")
            return []
    
    def _format_article(self, article: Dict[str, Any]) -> Dict[str, Any]:
        """Format a news article into a standardized dictionary.
        
        Args:
            article: News article object
            
        Returns:
            Formatted article data
        """
        return {
            'id': article['url'],
            'title': article['title'],
            'description': article['description'],
            'author': {
                'name': article['author']
            },
            'created_at': self._format_timestamp(article['publishedAt']),
            'source': {
                'id': article['source']['id'],
                'name': article['source']['name']
            },
            'url': article['url'],
            'media': {
                'type': 'image',
                'url': article['urlToImage']
            } if article.get('urlToImage') else None,
            'content': article['content']
        } 