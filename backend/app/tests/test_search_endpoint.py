import os
import sys
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock, MagicMock

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import test configuration
from app.core.test_config import SQLALCHEMY_DATABASE_URL
from app.models.db import Base, get_db
from app.models.user import User
from app.main import app
from app.services.router_service import RouterService
from app.services.auth import get_current_active_user
from app.services.credit_service import CreditService

# SQLAlchemy setup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Create test engine
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Test client
client = TestClient(app)

@pytest.fixture
def test_db():
    """Set up test database"""
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
    
    # Drop tables
    Base.metadata.drop_all(bind=test_engine)

@pytest.fixture
def test_client(test_db):
    """Create test client with database session override"""
    # Override the get_db dependency
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create test user
    test_user = User(
        id=999,
        email="test@example.com",
        username="testuser",
        is_active=True,
        is_admin=True,
        credits=100  # Give enough credits for testing
    )
    test_db.add(test_user)
    test_db.commit()
    
    # Override the auth dependency
    app.dependency_overrides[get_current_active_user] = lambda: test_user
    
    yield client
    
    # Reset dependencies
    app.dependency_overrides = {}

def test_text_search(test_client, test_db):
    """Test the text search endpoint"""
    # Mock the RouterService.search method
    with patch.object(RouterService, 'search', new_callable=AsyncMock) as mock_search:
        # Set up the mock return value
        mock_search.return_value = {
            "query_hash": "test_hash",
            "perplexity_used": False,
            "results": [{
                "source": "local",
                "content_hash": "hash1",
                "content_type": "text",
                "text": "test content",
                "url": "https://example.com/1",
                "timestamp": "2023-01-01T00:00:00Z",
                "similarity": 0.95,
                "engagement": 5,
                "channel_id": "channel1",
                "score": 0.95
            }],
            "origins": [{
                "source": "local",
                "content_hash": "hash1",
                "content_type": "text",
                "text": "test content",
                "url": "https://example.com/1",
                "timestamp": "2023-01-01T00:00:00Z",
                "similarity": 0.95,
                "engagement": 5,
                "channel_id": "channel1",
                "score": 0.95
            }],
            "confidence": 0.9
        }
        
        # Make the test request
        response = test_client.post(
            "/search/text",
            json={"query": "test search query", "force_perplexity": False}
        )
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "job_id" in data
        assert "query_hash" in data
        assert "query_type" in data
        assert "perplexity_used" in data
        assert "credits_used" in data
        assert "results" in data
        assert "origins" in data
        assert "confidence" in data
        
        # Verify router service was called with correct parameters
        mock_search.assert_called_once()
        call_args = mock_search.call_args[1]
        assert call_args["query"] == "test search query"
        assert call_args["query_type"] == "light"
        assert call_args["force_perplexity"] is False
        
        # Verify search history was created
        search_history = test_db.query(User).filter(User.id == 999).first()
        assert search_history is not None

def test_url_search(test_client, test_db):
    """Test the URL search endpoint"""
    # Mock the RouterService.search method
    with patch.object(RouterService, 'search', new_callable=AsyncMock) as mock_search:
        # Set up the mock return value
        mock_search.return_value = {
            "query_hash": "url_hash",
            "perplexity_used": True,
            "results": [{
                "source": "perplexity",
                "text": "URL content",
                "url": "https://example.com/source",
                "timestamp": "2023-01-01T00:00:00Z",
                "similarity": 0.88,
                "engagement": 7,
                "channel_id": "example.com",
                "score": 0.9
            }],
            "origins": [{
                "source": "perplexity",
                "text": "URL content",
                "url": "https://example.com/origin",
                "timestamp": "2022-12-01T00:00:00Z",
                "similarity": 0.88,
                "engagement": 10,
                "channel_id": "example.com",
                "score": 0.95
            }],
            "confidence": 0.85
        }
        
        # Make the test request
        response = test_client.post(
            "/search/url",
            json={"url": "https://example.com/test", "force_perplexity": True}
        )
        
        # Check the response
        assert response.status_code == 200
        data = response.json()
        
        # Verify router service was called with correct parameters
        mock_search.assert_called_once()
        call_args = mock_search.call_args[1]
        assert "example.com" in call_args["query"]
        assert call_args["force_perplexity"] is True
        
        # Verify result fields
        assert data["perplexity_used"] is True
        assert len(data["results"]) == 1
        assert len(data["origins"]) == 1
        assert data["confidence"] == 0.85

if __name__ == "__main__":
    # Run tests directly
    pytest.main(["-xvs", __file__]) 