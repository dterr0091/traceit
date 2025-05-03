from typing import Any, Dict, List, Optional
import praw
from .base import BaseAPIIntegration

class RedditIntegration(BaseAPIIntegration):
    """Reddit API integration."""
    
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        user_agent: str,
        username: Optional[str] = None,
        password: Optional[str] = None
    ):
        """Initialize Reddit API integration.
        
        Args:
            client_id: Reddit API client ID
            client_secret: Reddit API client secret
            user_agent: User agent string for API requests
            username: Reddit username (optional)
            password: Reddit password (optional)
        """
        super().__init__(client_id, client_secret)
        self.user_agent = user_agent
        self.username = username
        self.password = password
        self._client = None
    
    @property
    def client(self) -> praw.Reddit:
        """Get the Reddit API client instance."""
        if self._client is None:
            self._client = praw.Reddit(
                client_id=self.api_key,
                client_secret=self.api_secret,
                user_agent=self.user_agent,
                username=self.username,
                password=self.password
            )
        return self._client
    
    async def search_content(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Search for content on Reddit.
        
        Args:
            query: Search query string
            **kwargs: Additional search parameters
                - subreddit: Optional subreddit to search in
                - sort: Sort method ('relevance', 'hot', 'top', 'new', 'comments')
                - time_filter: Time filter ('all', 'day', 'week', 'month', 'year')
                - limit: Maximum number of results to return
                
        Returns:
            List of Reddit submissions matching the search criteria
        """
        try:
            subreddit = kwargs.get('subreddit')
            sort = kwargs.get('sort', 'relevance')
            time_filter = kwargs.get('time_filter', 'all')
            limit = kwargs.get('limit', 25)
            
            if subreddit:
                search_results = self.client.subreddit(subreddit).search(
                    query,
                    sort=sort,
                    time_filter=time_filter,
                    limit=limit
                )
            else:
                search_results = self.client.subreddit('all').search(
                    query,
                    sort=sort,
                    time_filter=time_filter,
                    limit=limit
                )
            
            return [self._format_submission(submission) for submission in search_results]
        except Exception as e:
            self._log_error(e, "Reddit search_content")
            return []
    
    async def get_content_details(self, content_id: str) -> Dict[str, Any]:
        """Get detailed information about a Reddit submission.
        
        Args:
            content_id: Reddit submission ID
            
        Returns:
            Detailed information about the submission
        """
        try:
            submission = self.client.submission(id=content_id)
            return self._format_submission(submission)
        except Exception as e:
            self._log_error(e, "Reddit get_content_details")
            return {}
    
    async def get_user_content(self, username: str, **kwargs) -> List[Dict[str, Any]]:
        """Get content posted by a Reddit user.
        
        Args:
            username: Reddit username
            **kwargs: Additional parameters
                - content_type: Type of content ('submissions', 'comments')
                - sort: Sort method ('new', 'hot', 'top', 'controversial')
                - time_filter: Time filter ('all', 'day', 'week', 'month', 'year')
                - limit: Maximum number of results to return
                
        Returns:
            List of content items posted by the user
        """
        try:
            content_type = kwargs.get('content_type', 'submissions')
            sort = kwargs.get('sort', 'new')
            time_filter = kwargs.get('time_filter', 'all')
            limit = kwargs.get('limit', 25)
            
            redditor = self.client.redditor(username)
            
            if content_type == 'submissions':
                content = redditor.submissions.new(limit=limit)
            else:
                content = redditor.comments.new(limit=limit)
            
            return [self._format_submission(item) for item in content]
        except Exception as e:
            self._log_error(e, "Reddit get_user_content")
            return []
    
    def _format_submission(self, submission: Any) -> Dict[str, Any]:
        """Format a Reddit submission into a standardized dictionary.
        
        Args:
            submission: PRAW submission object
            
        Returns:
            Formatted submission data
        """
        return {
            'id': submission.id,
            'title': submission.title,
            'author': submission.author.name if submission.author else '[deleted]',
            'created_utc': self._format_timestamp(submission.created_utc),
            'score': submission.score,
            'upvote_ratio': submission.upvote_ratio,
            'num_comments': submission.num_comments,
            'subreddit': submission.subreddit.display_name,
            'url': submission.url,
            'permalink': f"https://reddit.com{submission.permalink}",
            'is_self': submission.is_self,
            'selftext': submission.selftext if submission.is_self else None,
            'media': {
                'type': 'image' if submission.url.endswith(('.jpg', '.jpeg', '.png', '.gif')) else 'video',
                'url': submission.url
            } if not submission.is_self else None
        } 