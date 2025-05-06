import os
import sys
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import test configuration
from app.core.test_config import SQLALCHEMY_DATABASE_URL
from app.models.db import Base
from app.models.user import User, SearchHistory

# Create test engine
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

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

def test_create_user(test_db):
    """Test that we can create a user in the database"""
    # Create test user
    test_user = User(
        email="test@example.com",
        username="testuser",
        is_active=True,
        is_admin=False
    )
    
    # Add to database
    test_db.add(test_user)
    test_db.commit()
    test_db.refresh(test_user)
    
    # Verify user was created
    assert test_user.id is not None
    assert test_user.email == "test@example.com"
    
    # Query the user
    db_user = test_db.query(User).filter(User.email == "test@example.com").first()
    assert db_user is not None
    assert db_user.username == "testuser"
    
    return True

def test_create_search_history(test_db):
    """Test that we can create search history records"""
    # Create test user first
    test_user = User(
        email="search@example.com",
        username="searchuser",
        is_active=True
    )
    test_db.add(test_user)
    test_db.commit()
    test_db.refresh(test_user)
    
    # Create search history record
    search_record = SearchHistory(
        user_id=test_user.id,
        query_hash="test_hash_123",
        query_type="light",
        credits_used=1,
        perplexity_used=False
    )
    test_db.add(search_record)
    test_db.commit()
    test_db.refresh(search_record)
    
    # Verify record was created
    assert search_record.id is not None
    assert search_record.query_hash == "test_hash_123"
    
    # Query the search history
    db_search = test_db.query(SearchHistory).filter(
        SearchHistory.user_id == test_user.id
    ).first()
    assert db_search is not None
    assert db_search.query_type == "light"
    
    return True

if __name__ == "__main__":
    # Run tests directly
    pytest.main(["-xvs", __file__]) 