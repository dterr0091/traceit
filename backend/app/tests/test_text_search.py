import os
import sys
import pytest
import asyncio
from unittest.mock import patch, AsyncMock, MagicMock
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import test configuration to set up environment
from app.core.test_config import SQLALCHEMY_DATABASE_URL

# Import services after setting up paths
from app.services.router_service import RouterService
from app.services.vector_service import VectorService
from app.services.perplexity_service import perplexity_service
from app.services.redis_service import redis_service

# Import DB models for test fixture
from app.models.db import Base, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Create test engine with SQLite in-memory database
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

@pytest.fixture(scope="function")
def test_db():
    """Set up a fresh test database for each test."""
    # Create the tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create a test session
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
    
    # Drop tables after test
    Base.metadata.drop_all(bind=test_engine)

@pytest.mark.asyncio
async def test_router_service_search(test_db):
    """
    Test if a search will complete successfully using the RouterService directly.
    This test mocks the dependencies to isolate just the search functionality.
    """
    logger.info("Testing RouterService.search functionality")
    
    # Mock the VectorService
    with patch.object(VectorService, 'search_similar_content') as mock_vector_search:
        # Set up mock to return some search results
        mock_vector_search.return_value = [
            {
                "content_hash": "test_hash_1",
                "content_type": "text",
                "raw_text": "This is a test document",
                "source_url": "https://example.com/doc1",
                "timestamp": "2023-01-01T00:00:00Z",
                "similarity": 0.92,
                "engagement_score": 5,
                "channel_id": "channel1"
            }
        ]
        
        # Mock the Redis service
        with patch.object(redis_service, 'get_cache', return_value=None) as mock_get_cache:
            with patch.object(redis_service, 'set_cache') as mock_set_cache:
                # Mock perplexity service to return empty results
                with patch.object(perplexity_service, 'search', new_callable=AsyncMock) as mock_perplexity:
                    mock_perplexity.return_value = {
                        "results": [
                            {
                                "url": "https://example.com/perplexity1",
                                "title": "Test Perplexity Result",
                                "snippet": "This is a test snippet from Perplexity",
                                "relevance_score": 0.85,
                                "freshness_score": 0.75,
                                "published_date": "2023-01-02T00:00:00Z",
                                "domain": "example.com",
                                "id": "test_perplexity_id_1",
                                "engagement_score": 4
                            }
                        ]
                    }
                    
                    # Test query
                    test_query = "test search query"
                    
                    # Call the search method with our test database
                    result = await RouterService.search(
                        db=test_db,
                        query=test_query,
                        query_type="light",
                        force_perplexity=False
                    )
                    
                    # Verify response structure
                    assert "query_hash" in result
                    assert "perplexity_used" in result
                    assert "results" in result
                    assert "origins" in result
                    assert "confidence" in result
                    
                    # Verify that results were returned
                    assert len(result["results"]) > 0
                    
                    # Check that vector service was called
                    mock_vector_search.assert_called_once()
                    
                    # Log success
                    logger.info("Search test completed successfully!")
                    logger.info(f"Results: {len(result['results'])} items, confidence: {result['confidence']}")
                    return True

async def main():
    """Run the test using direct call - creates a test DB session"""
    logger.info("Starting text search test")
    
    # Create tables for direct testing
    Base.metadata.create_all(bind=test_engine)
    
    # Create a test session
    db = TestingSessionLocal()
    
    try:
        # Use pytest to ensure test runs with async support
        import pytest
        exitcode = pytest.main(["-xvs", __file__])
        logger.info(f"Test completed with exit code: {exitcode}")
    finally:
        db.close()
        # Clean up
        Base.metadata.drop_all(bind=test_engine)

if __name__ == "__main__":
    # Run the test directly
    asyncio.run(main()) 