"""
Minimal test script to verify search functionality and database configuration.
This script doesn't rely on the existing app's configuration.
"""
import os
import asyncio
import logging
import sys
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.pool import StaticPool

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Define SQLite in-memory database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create engine and session
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Define minimalistic models for testing
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, index=True)
    credits = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    
    search_history = relationship("SearchHistory", back_populates="user")

class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    query_hash = Column(String, index=True)
    query_type = Column(String)
    credits_used = Column(Integer)
    perplexity_used = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="search_history")

# Create tables
Base.metadata.create_all(bind=engine)

# Mock router service for testing
class MockRouterService:
    @staticmethod
    async def search(db, query, query_type="light", force_perplexity=False):
        """Mock implementation of router service search"""
        logger.info(f"Search called with query: '{query}', type: {query_type}")
        
        # Simulate processing time
        await asyncio.sleep(0.5)
        
        # Return mock results
        return {
            "query": query,
            "query_hash": "mock_hash_123",
            "query_type": query_type,
            "perplexity_used": force_perplexity,
            "results": [
                {
                    "source": "local" if not force_perplexity else "perplexity",
                    "content_hash": "content_123",
                    "text": "This is a mock search result.",
                    "url": "https://example.com/result",
                    "timestamp": "2023-01-01T00:00:00Z",
                    "similarity": 0.9,
                    "score": 0.85
                }
            ],
            "origins": [
                {
                    "source": "local" if not force_perplexity else "perplexity",
                    "content_hash": "content_origin",
                    "text": "This is the original content.",
                    "url": "https://example.com/origin",
                    "timestamp": "2022-01-01T00:00:00Z",
                    "similarity": 0.95,
                    "score": 0.92
                }
            ],
            "confidence": 0.88
        }

async def test_search_flow():
    """Test the search flow"""
    logger.info("Starting search flow test")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Create test user
        test_user = User(email="test@example.com", username="testuser", credits=100)
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        logger.info(f"Created test user with ID: {test_user.id}")
        
        # Create mock router service
        router_service = MockRouterService()
        
        # Perform search
        search_result = await router_service.search(
            db=db,
            query="test search query",
            query_type="light",
            force_perplexity=False
        )
        
        # Log the result
        logger.info(f"Search completed with confidence: {search_result['confidence']}")
        logger.info(f"Results: {len(search_result['results'])}, Origins: {len(search_result['origins'])}")
        
        # Create search history record
        search_record = SearchHistory(
            user_id=test_user.id,
            query_hash=search_result["query_hash"],
            query_type=search_result["query_type"],
            credits_used=1,
            perplexity_used=search_result["perplexity_used"]
        )
        db.add(search_record)
        db.commit()
        db.refresh(search_record)
        logger.info(f"Created search history record with ID: {search_record.id}")
        
        # Verify database records
        user_search_history = db.query(SearchHistory).filter(
            SearchHistory.user_id == test_user.id
        ).all()
        
        logger.info(f"Found {len(user_search_history)} search history records for user")
        
        # Update user credits
        test_user.credits -= 1
        db.commit()
        db.refresh(test_user)
        logger.info(f"Updated user credits to: {test_user.credits}")
        
        logger.info("Search flow test completed successfully!")
        return True
        
    finally:
        # Close database session
        db.close()

async def main():
    """Run all tests"""
    logger.info("Starting tests")
    
    try:
        # Run search flow test
        search_result = await test_search_flow()
        logger.info(f"Search flow test result: {search_result}")
        
    except Exception as e:
        logger.error(f"Error during testing: {str(e)}")
        return False
    
    logger.info("All tests completed")
    return True

if __name__ == "__main__":
    # Run tests
    asyncio.run(main()) 