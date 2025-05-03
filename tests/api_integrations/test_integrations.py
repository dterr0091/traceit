import pytest
from unittest.mock import Mock, patch
from services.api_integrations import APIIntegrationFactory

@pytest.fixture
def mock_reddit_client():
    with patch('praw.Reddit') as mock:
        yield mock

@pytest.fixture
def mock_twitter_client():
    with patch('tweepy.Client') as mock:
        yield mock

@pytest.fixture
def mock_instagram_client():
    with patch('instaloader.Instaloader') as mock:
        yield mock

@pytest.fixture
def mock_youtube_client():
    with patch('googleapiclient.discovery.build') as mock:
        yield mock

@pytest.fixture
def mock_news_client():
    with patch('newsapi.NewsApiClient') as mock:
        yield mock

def test_factory_supported_platforms():
    """Test that the factory returns the correct list of supported platforms."""
    platforms = APIIntegrationFactory.get_supported_platforms()
    assert set(platforms) == {'reddit', 'twitter', 'instagram', 'youtube', 'news'}

def test_factory_required_credentials():
    """Test that the factory returns the correct required credentials for each platform."""
    credentials = {
        'reddit': ['client_id', 'client_secret', 'user_agent', 'username', 'password'],
        'twitter': ['consumer_key', 'consumer_secret', 'access_token', 'access_token_secret'],
        'instagram': ['username', 'password'],
        'youtube': ['api_key'],
        'news': ['api_key']
    }
    
    for platform, expected in credentials.items():
        assert set(APIIntegrationFactory.get_required_credentials(platform)) == set(expected)

def test_factory_create_integration():
    """Test that the factory creates the correct integration instances."""
    # Test Reddit integration
    reddit = APIIntegrationFactory.create_integration(
        'reddit',
        client_id='test_id',
        client_secret='test_secret',
        user_agent='test_agent',
        username='test_user',
        password='test_pass'
    )
    assert isinstance(reddit, reddit.__class__)
    
    # Test Twitter integration
    twitter = APIIntegrationFactory.create_integration(
        'twitter',
        consumer_key='test_key',
        consumer_secret='test_secret',
        access_token='test_token',
        access_token_secret='test_token_secret'
    )
    assert isinstance(twitter, twitter.__class__)
    
    # Test Instagram integration
    instagram = APIIntegrationFactory.create_integration(
        'instagram',
        username='test_user',
        password='test_pass'
    )
    assert isinstance(instagram, instagram.__class__)
    
    # Test YouTube integration
    youtube = APIIntegrationFactory.create_integration(
        'youtube',
        api_key='test_key'
    )
    assert isinstance(youtube, youtube.__class__)
    
    # Test News integration
    news = APIIntegrationFactory.create_integration(
        'news',
        api_key='test_key'
    )
    assert isinstance(news, news.__class__)

def test_factory_invalid_platform():
    """Test that the factory raises ValueError for invalid platforms."""
    with pytest.raises(ValueError):
        APIIntegrationFactory.create_integration('invalid_platform')

@pytest.mark.asyncio
async def test_reddit_search_content(mock_reddit_client):
    """Test Reddit search_content method."""
    # Setup mock
    mock_submission = Mock()
    mock_submission.id = 'test_id'
    mock_submission.title = 'Test Title'
    mock_submission.author = Mock()
    mock_submission.author.name = 'test_author'
    mock_submission.created_utc = 1234567890
    mock_submission.score = 100
    mock_submission.upvote_ratio = 0.95
    mock_submission.num_comments = 50
    mock_submission.subreddit = Mock()
    mock_submission.subreddit.display_name = 'test_subreddit'
    mock_submission.url = 'https://test.com'
    mock_submission.permalink = '/r/test_subreddit/test_id'
    mock_submission.is_self = False
    
    mock_reddit_client.return_value.subreddit.return_value.search.return_value = [mock_submission]
    
    # Create integration and test
    reddit = APIIntegrationFactory.create_integration(
        'reddit',
        client_id='test_id',
        client_secret='test_secret',
        user_agent='test_agent'
    )
    
    results = await reddit.search_content('test query')
    assert len(results) == 1
    assert results[0]['id'] == 'test_id'
    assert results[0]['title'] == 'Test Title'
    assert results[0]['author'] == 'test_author'

@pytest.mark.asyncio
async def test_twitter_search_content(mock_twitter_client):
    """Test Twitter search_content method."""
    # Setup mock
    mock_tweet = Mock()
    mock_tweet.id = 'test_id'
    mock_tweet.text = 'Test tweet'
    mock_tweet.author_id = 'test_author_id'
    mock_tweet.author = Mock()
    mock_tweet.author.username = 'test_user'
    mock_tweet.author.name = 'Test User'
    mock_tweet.author.profile_image_url = 'https://test.com/profile.jpg'
    mock_tweet.created_at = '2023-01-01T00:00:00Z'
    mock_tweet.public_metrics = {
        'retweet_count': 100,
        'reply_count': 50,
        'like_count': 200,
        'quote_count': 30
    }
    mock_tweet.attachments = {'media': []}
    
    mock_twitter_client.return_value.search_recent_tweets.return_value = Mock(data=[mock_tweet])
    
    # Create integration and test
    twitter = APIIntegrationFactory.create_integration(
        'twitter',
        consumer_key='test_key',
        consumer_secret='test_secret'
    )
    
    results = await twitter.search_content('test query')
    assert len(results) == 1
    assert results[0]['id'] == 'test_id'
    assert results[0]['text'] == 'Test tweet'
    assert results[0]['author']['username'] == 'test_user'

@pytest.mark.asyncio
async def test_instagram_search_content(mock_instagram_client):
    """Test Instagram search_content method."""
    # Setup mock
    mock_post = Mock()
    mock_post.shortcode = 'test_shortcode'
    mock_post.caption = 'Test caption'
    mock_post.owner_username = 'test_user'
    mock_post.owner_profile = Mock()
    mock_post.owner_profile.full_name = 'Test User'
    mock_post.owner_profile.profile_pic_url = 'https://test.com/profile.jpg'
    mock_post.date = '2023-01-01T00:00:00Z'
    mock_post.likes = 100
    mock_post.comments = 50
    mock_post.url = 'https://test.com/post.jpg'
    mock_post.is_video = False
    mock_post.location = None
    
    mock_instagram_client.return_value.search_posts.return_value = [mock_post]
    
    # Create integration and test
    instagram = APIIntegrationFactory.create_integration(
        'instagram',
        username='test_user',
        password='test_pass'
    )
    
    results = await instagram.search_content('test query')
    assert len(results) == 1
    assert results[0]['id'] == 'test_shortcode'
    assert results[0]['caption'] == 'Test caption'
    assert results[0]['author']['username'] == 'test_user'

@pytest.mark.asyncio
async def test_youtube_search_content(mock_youtube_client):
    """Test YouTube search_content method."""
    # Setup mock
    mock_video = {
        'id': 'test_id',
        'snippet': {
            'title': 'Test Video',
            'description': 'Test description',
            'channelId': 'test_channel_id',
            'channelTitle': 'Test Channel',
            'publishedAt': '2023-01-01T00:00:00Z',
            'thumbnails': {
                'high': {
                    'url': 'https://test.com/thumbnail.jpg'
                }
            }
        },
        'statistics': {
            'viewCount': '1000',
            'likeCount': '100',
            'commentCount': '50'
        },
        'contentDetails': {
            'duration': 'PT5M30S'
        }
    }
    
    mock_youtube_client.return_value.search.return_value.list.return_value.execute.return_value = {
        'items': [{'id': {'videoId': 'test_id'}}]
    }
    mock_youtube_client.return_value.videos.return_value.list.return_value.execute.return_value = {
        'items': [mock_video]
    }
    
    # Create integration and test
    youtube = APIIntegrationFactory.create_integration(
        'youtube',
        api_key='test_key'
    )
    
    results = await youtube.search_content('test query')
    assert len(results) == 1
    assert results[0]['id'] == 'test_id'
    assert results[0]['title'] == 'Test Video'
    assert results[0]['author']['id'] == 'test_channel_id'

@pytest.mark.asyncio
async def test_news_search_content(mock_news_client):
    """Test News API search_content method."""
    # Setup mock
    mock_article = {
        'url': 'https://test.com/article',
        'title': 'Test Article',
        'description': 'Test description',
        'author': 'Test Author',
        'publishedAt': '2023-01-01T00:00:00Z',
        'source': {
            'id': 'test-source',
            'name': 'Test Source'
        },
        'urlToImage': 'https://test.com/image.jpg',
        'content': 'Test content'
    }
    
    mock_news_client.return_value.get_everything.return_value = {
        'articles': [mock_article]
    }
    
    # Create integration and test
    news = APIIntegrationFactory.create_integration(
        'news',
        api_key='test_key'
    )
    
    results = await news.search_content('test query')
    assert len(results) == 1
    assert results[0]['id'] == 'https://test.com/article'
    assert results[0]['title'] == 'Test Article'
    assert results[0]['author']['name'] == 'Test Author' 