import pytest
from datetime import datetime
from typing import List, Optional
from services.search_service import SearchService, SearchResult, SearchInput

@pytest.fixture
def search_service():
    return SearchService()

@pytest.fixture
def mock_search_input():
    return SearchInput(
        text="test query",
        image_urls=[],
        urls=[],
        max_results=4
    )

def test_search_with_text(search_service, mock_search_input):
    """Test search functionality with text input."""
    results = search_service.search(mock_search_input)
    
    assert isinstance(results, list)
    assert len(results) <= mock_search_input.max_results
    for result in results:
        assert isinstance(result, SearchResult)
        assert result.title
        assert result.url
        assert result.platform
        assert result.timestamp
        assert result.virality_score >= 0

def test_search_with_image(search_service):
    """Test search functionality with image input."""
    input_data = SearchInput(
        text="",
        image_urls=["https://example.com/image.jpg"],
        urls=[],
        max_results=4
    )
    results = search_service.search(input_data)
    
    assert isinstance(results, list)
    assert len(results) <= input_data.max_results

def test_search_with_url(search_service):
    """Test search functionality with URL input."""
    input_data = SearchInput(
        text="",
        image_urls=[],
        urls=["https://example.com/article"],
        max_results=4
    )
    results = search_service.search(input_data)
    
    assert isinstance(results, list)
    assert len(results) <= input_data.max_results

def test_search_with_multiple_inputs(search_service):
    """Test search functionality with multiple input types."""
    input_data = SearchInput(
        text="test query",
        image_urls=["https://example.com/image.jpg"],
        urls=["https://example.com/article"],
        max_results=4
    )
    results = search_service.search(input_data)
    
    assert isinstance(results, list)
    assert len(results) <= input_data.max_results

def test_search_with_invalid_input(search_service):
    """Test search functionality with invalid input."""
    with pytest.raises(ValueError):
        search_service.search(SearchInput(
            text="",
            image_urls=[],
            urls=[],
            max_results=4
        )) 