import os
import pytest
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime
from typing import List, Optional

# Set up environment variables before importing any modules
os.environ["OPENAI_API_KEY"] = "test_key"
os.environ["PERPLEXITY_API_KEY"] = "test_key"
os.environ["OPENAI_MODEL"] = "gpt-4"

from services.search_service import SearchService, SearchResult, SearchInput

@pytest.fixture
def mock_openai_service():
    with patch('services.search_service.OpenAIService') as mock:
        mock_instance = Mock()
        mock_instance.analyze_content.return_value = {
            "originalSources": [{"title": "Test Source", "url": "https://test.com", "platform": "Web"}],
            "viralPoints": [{"title": "Test Viral", "url": "https://viral.com", "platform": "Twitter"}]
        }
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_perplexity_api():
    with patch('services.search_service.PerplexityAPI') as mock:
        mock_instance = AsyncMock()
        mock_instance.search.return_value = [
            {
                "title": "Test Result",
                "url": "https://test.com",
                "platform": "Web",
                "timestamp": "2024-03-15T10:30:00",
                "virality_score": 0.8,
                "snippet": "Test snippet",
                "image_url": "https://test.com/image.jpg"
            }
        ]
        mock.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def search_service(mock_openai_service, mock_perplexity_api):
    return SearchService()

@pytest.mark.asyncio
async def test_search_with_text(search_service):
    """Test search functionality with text input."""
    input_data = SearchInput(
        text="test query",
        image_urls=[],
        urls=[],
        max_results=4
    )
    
    results = await search_service.search(input_data)
    
    assert isinstance(results, list)
    assert len(results) > 0
    assert isinstance(results[0], SearchResult)
    assert results[0].title == "Test Result"
    assert str(results[0].url).rstrip('/') == "https://test.com"
    assert results[0].platform == "Web"

@pytest.mark.asyncio
async def test_search_with_image(search_service):
    """Test search functionality with image input."""
    input_data = SearchInput(
        text="",
        image_urls=["https://example.com/image.jpg"],
        urls=[],
        max_results=4
    )
    
    results = await search_service.search(input_data)
    
    assert isinstance(results, list)
    assert len(results) > 0
    assert isinstance(results[0], SearchResult)

@pytest.mark.asyncio
async def test_search_with_invalid_input(search_service):
    """Test search functionality with invalid input."""
    with pytest.raises(ValueError):
        await search_service.search(SearchInput(
            text="",
            image_urls=[],
            urls=[],
            max_results=4
        )) 