from typing import Any, Dict, List, Optional
import instaloader
from datetime import datetime
from .base import BaseAPIIntegration

class InstagramIntegration(BaseAPIIntegration):
    """Instagram API integration."""
    
    def __init__(
        self,
        username: str,
        password: str
    ):
        """Initialize Instagram API integration.
        
        Args:
            username: Instagram username
            password: Instagram password
        """
        super().__init__(username, password)
        self._client = None
    
    @property
    def client(self) -> instaloader.Instaloader:
        """Get the Instagram API client instance."""
        if self._client is None:
            self._client = instaloader.Instaloader()
            self._client.login(self.api_key, self.api_secret)
        return self._client
    
    async def search_content(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Search for Instagram posts.
        
        Args:
            query: Search query string
            **kwargs: Additional search parameters
                - max_results: Maximum number of results to return (default: 10)
                - post_type: Type of post ('image', 'video', 'all')
                
        Returns:
            List of Instagram posts matching the search criteria
        """
        try:
            max_results = kwargs.get('max_results', 10)
            post_type = kwargs.get('post_type', 'all')
            
            posts = []
            for post in self.client.search_posts(query):
                if len(posts) >= max_results:
                    break
                    
                if post_type == 'all' or (
                    post_type == 'image' and not post.is_video
                ) or (
                    post_type == 'video' and post.is_video
                ):
                    posts.append(self._format_post(post))
            
            return posts
        except Exception as e:
            self._log_error(e, "Instagram search_content")
            return []
    
    async def get_content_details(self, shortcode: str) -> Dict[str, Any]:
        """Get detailed information about an Instagram post.
        
        Args:
            shortcode: Instagram post shortcode
            
        Returns:
            Detailed information about the post
        """
        try:
            post = instaloader.Post.from_shortcode(self.client.context, shortcode)
            return self._format_post(post)
        except Exception as e:
            self._log_error(e, "Instagram get_content_details")
            return {}
    
    async def get_user_content(self, username: str, **kwargs) -> List[Dict[str, Any]]:
        """Get posts from a specific Instagram user.
        
        Args:
            username: Instagram username
            **kwargs: Additional parameters
                - max_results: Maximum number of results to return (default: 10)
                - post_type: Type of post ('image', 'video', 'all')
                
        Returns:
            List of posts from the user
        """
        try:
            max_results = kwargs.get('max_results', 10)
            post_type = kwargs.get('post_type', 'all')
            
            profile = instaloader.Profile.from_username(self.client.context, username)
            posts = []
            
            for post in profile.get_posts():
                if len(posts) >= max_results:
                    break
                    
                if post_type == 'all' or (
                    post_type == 'image' and not post.is_video
                ) or (
                    post_type == 'video' and post.is_video
                ):
                    posts.append(self._format_post(post))
            
            return posts
        except Exception as e:
            self._log_error(e, "Instagram get_user_content")
            return []
    
    def _format_post(self, post: Any) -> Dict[str, Any]:
        """Format an Instagram post into a standardized dictionary.
        
        Args:
            post: Instagram post object
            
        Returns:
            Formatted post data
        """
        return {
            'id': post.shortcode,
            'caption': post.caption,
            'author': {
                'username': post.owner_username,
                'full_name': post.owner_profile.full_name,
                'profile_pic_url': post.owner_profile.profile_pic_url
            },
            'created_at': self._format_timestamp(post.date),
            'metrics': {
                'likes': post.likes,
                'comments': post.comments
            },
            'url': f"https://instagram.com/p/{post.shortcode}",
            'media': {
                'type': 'video' if post.is_video else 'image',
                'url': post.url,
                'thumbnail_url': post.thumbnail_url if post.is_video else None,
                'video_url': post.video_url if post.is_video else None
            },
            'location': {
                'name': post.location.name if post.location else None,
                'lat': post.location.lat if post.location else None,
                'lng': post.location.lng if post.location else None
            } if post.location else None
        } 