from typing import Any, Dict, List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .base import BaseAPIIntegration

class YouTubeIntegration(BaseAPIIntegration):
    """YouTube API integration."""
    
    def __init__(self, api_key: str):
        """Initialize YouTube API integration.
        
        Args:
            api_key: YouTube API key
        """
        super().__init__(api_key, None)
        self._client = None
    
    @property
    def client(self) -> Any:
        """Get the YouTube API client instance."""
        if self._client is None:
            self._client = build('youtube', 'v3', developerKey=self.api_key)
        return self._client
    
    async def search_content(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Search for YouTube videos.
        
        Args:
            query: Search query string
            **kwargs: Additional search parameters
                - max_results: Maximum number of results to return (default: 10)
                - order: Sort order ('date', 'rating', 'relevance', 'title', 'videoCount', 'viewCount')
                - type: Content type ('video', 'channel', 'playlist')
                
        Returns:
            List of YouTube videos matching the search criteria
        """
        try:
            max_results = kwargs.get('max_results', 10)
            order = kwargs.get('order', 'relevance')
            content_type = kwargs.get('type', 'video')
            
            search_response = self.client.search().list(
                q=query,
                part='snippet',
                maxResults=max_results,
                order=order,
                type=content_type
            ).execute()
            
            video_ids = [item['id']['videoId'] for item in search_response['items']]
            
            # Get video details
            videos_response = self.client.videos().list(
                part='snippet,statistics,contentDetails',
                id=','.join(video_ids)
            ).execute()
            
            return [self._format_video(video) for video in videos_response['items']]
        except HttpError as e:
            self._log_error(e, "YouTube search_content")
            return []
    
    async def get_content_details(self, video_id: str) -> Dict[str, Any]:
        """Get detailed information about a YouTube video.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            Detailed information about the video
        """
        try:
            video_response = self.client.videos().list(
                part='snippet,statistics,contentDetails',
                id=video_id
            ).execute()
            
            if not video_response['items']:
                return {}
                
            return self._format_video(video_response['items'][0])
        except HttpError as e:
            self._log_error(e, "YouTube get_content_details")
            return {}
    
    async def get_user_content(self, channel_id: str, **kwargs) -> List[Dict[str, Any]]:
        """Get videos from a specific YouTube channel.
        
        Args:
            channel_id: YouTube channel ID
            **kwargs: Additional parameters
                - max_results: Maximum number of results to return (default: 10)
                - order: Sort order ('date', 'rating', 'relevance', 'title', 'videoCount', 'viewCount')
                
        Returns:
            List of videos from the channel
        """
        try:
            max_results = kwargs.get('max_results', 10)
            order = kwargs.get('order', 'date')
            
            # Get channel's uploads playlist ID
            channel_response = self.client.channels().list(
                part='contentDetails',
                id=channel_id
            ).execute()
            
            if not channel_response['items']:
                return []
                
            uploads_playlist_id = channel_response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
            
            # Get videos from uploads playlist
            playlist_response = self.client.playlistItems().list(
                part='snippet',
                playlistId=uploads_playlist_id,
                maxResults=max_results
            ).execute()
            
            video_ids = [item['snippet']['resourceId']['videoId'] for item in playlist_response['items']]
            
            # Get video details
            videos_response = self.client.videos().list(
                part='snippet,statistics,contentDetails',
                id=','.join(video_ids)
            ).execute()
            
            return [self._format_video(video) for video in videos_response['items']]
        except HttpError as e:
            self._log_error(e, "YouTube get_user_content")
            return []
    
    def _format_video(self, video: Dict[str, Any]) -> Dict[str, Any]:
        """Format a YouTube video into a standardized dictionary.
        
        Args:
            video: YouTube video object
            
        Returns:
            Formatted video data
        """
        snippet = video['snippet']
        statistics = video['statistics']
        content_details = video['contentDetails']
        
        return {
            'id': video['id'],
            'title': snippet['title'],
            'description': snippet['description'],
            'author': {
                'id': snippet['channelId'],
                'name': snippet['channelTitle']
            },
            'created_at': self._format_timestamp(snippet['publishedAt']),
            'metrics': {
                'view_count': int(statistics.get('viewCount', 0)),
                'like_count': int(statistics.get('likeCount', 0)),
                'comment_count': int(statistics.get('commentCount', 0))
            },
            'url': f"https://www.youtube.com/watch?v={video['id']}",
            'media': {
                'type': 'video',
                'duration': content_details['duration'],
                'thumbnail_url': snippet['thumbnails']['high']['url']
            },
            'tags': snippet.get('tags', [])
        } 