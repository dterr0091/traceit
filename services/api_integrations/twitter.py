from typing import Any, Dict, List, Optional
import tweepy
from .base import BaseAPIIntegration

class TwitterIntegration(BaseAPIIntegration):
    """Twitter API integration."""
    
    def __init__(
        self,
        consumer_key: str,
        consumer_secret: str,
        access_token: Optional[str] = None,
        access_token_secret: Optional[str] = None
    ):
        """Initialize Twitter API integration.
        
        Args:
            consumer_key: Twitter API consumer key
            consumer_secret: Twitter API consumer secret
            access_token: Twitter API access token (optional)
            access_token_secret: Twitter API access token secret (optional)
        """
        super().__init__(consumer_key, consumer_secret)
        self.access_token = access_token
        self.access_token_secret = access_token_secret
        self._client = None
    
    @property
    def client(self) -> tweepy.Client:
        """Get the Twitter API client instance."""
        if self._client is None:
            self._client = tweepy.Client(
                consumer_key=self.api_key,
                consumer_secret=self.api_secret,
                access_token=self.access_token,
                access_token_secret=self.access_token_secret
            )
        return self._client
    
    async def search_content(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Search for tweets.
        
        Args:
            query: Search query string
            **kwargs: Additional search parameters
                - max_results: Maximum number of results to return (default: 10)
                - start_time: Start time for search (ISO 8601 format)
                - end_time: End time for search (ISO 8601 format)
                - sort_order: Sort order ('recency' or 'relevancy')
                
        Returns:
            List of tweets matching the search criteria
        """
        try:
            max_results = kwargs.get('max_results', 10)
            start_time = kwargs.get('start_time')
            end_time = kwargs.get('end_time')
            sort_order = kwargs.get('sort_order', 'recency')
            
            tweets = self.client.search_recent_tweets(
                query=query,
                max_results=max_results,
                start_time=start_time,
                end_time=end_time,
                sort_order=sort_order,
                tweet_fields=['created_at', 'public_metrics', 'entities', 'attachments'],
                user_fields=['username', 'name', 'profile_image_url'],
                expansions=['author_id', 'attachments.media_keys'],
                media_fields=['url', 'preview_image_url', 'type']
            )
            
            return [self._format_tweet(tweet) for tweet in tweets.data]
        except Exception as e:
            self._log_error(e, "Twitter search_content")
            return []
    
    async def get_content_details(self, tweet_id: str) -> Dict[str, Any]:
        """Get detailed information about a tweet.
        
        Args:
            tweet_id: Tweet ID
            
        Returns:
            Detailed information about the tweet
        """
        try:
            tweet = self.client.get_tweet(
                id=tweet_id,
                tweet_fields=['created_at', 'public_metrics', 'entities', 'attachments'],
                user_fields=['username', 'name', 'profile_image_url'],
                expansions=['author_id', 'attachments.media_keys'],
                media_fields=['url', 'preview_image_url', 'type']
            )
            return self._format_tweet(tweet.data)
        except Exception as e:
            self._log_error(e, "Twitter get_content_details")
            return {}
    
    async def get_user_content(self, username: str, **kwargs) -> List[Dict[str, Any]]:
        """Get tweets from a specific user.
        
        Args:
            username: Twitter username
            **kwargs: Additional parameters
                - max_results: Maximum number of results to return (default: 10)
                - start_time: Start time for search (ISO 8601 format)
                - end_time: End time for search (ISO 8601 format)
                
        Returns:
            List of tweets from the user
        """
        try:
            max_results = kwargs.get('max_results', 10)
            start_time = kwargs.get('start_time')
            end_time = kwargs.get('end_time')
            
            user = self.client.get_user(username=username)
            tweets = self.client.get_users_tweets(
                id=user.data.id,
                max_results=max_results,
                start_time=start_time,
                end_time=end_time,
                tweet_fields=['created_at', 'public_metrics', 'entities', 'attachments'],
                user_fields=['username', 'name', 'profile_image_url'],
                expansions=['author_id', 'attachments.media_keys'],
                media_fields=['url', 'preview_image_url', 'type']
            )
            
            return [self._format_tweet(tweet) for tweet in tweets.data]
        except Exception as e:
            self._log_error(e, "Twitter get_user_content")
            return []
    
    def _format_tweet(self, tweet: Any) -> Dict[str, Any]:
        """Format a tweet into a standardized dictionary.
        
        Args:
            tweet: Tweet object
            
        Returns:
            Formatted tweet data
        """
        return {
            'id': tweet.id,
            'text': tweet.text,
            'author': {
                'id': tweet.author_id,
                'username': tweet.author.username,
                'name': tweet.author.name,
                'profile_image_url': tweet.author.profile_image_url
            },
            'created_at': self._format_timestamp(tweet.created_at),
            'metrics': {
                'retweet_count': tweet.public_metrics['retweet_count'],
                'reply_count': tweet.public_metrics['reply_count'],
                'like_count': tweet.public_metrics['like_count'],
                'quote_count': tweet.public_metrics['quote_count']
            },
            'url': f"https://twitter.com/{tweet.author.username}/status/{tweet.id}",
            'media': [{
                'type': media.type,
                'url': media.url or media.preview_image_url
            } for media in tweet.attachments.get('media', [])] if hasattr(tweet, 'attachments') else []
        } 