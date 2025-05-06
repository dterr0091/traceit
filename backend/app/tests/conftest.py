import os
import sys
import pytest
from typing import Any, Generator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import test config first to set environment variables
from app.core.test_config import SQLALCHEMY_DATABASE_URL
from app.models.db import Base
from app.main import app
from app.models.db import get_db

# Create test database engine - using SQLite in-memory database
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

# Create test session
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def test_db() -> Generator:
    """
    Create a fresh database for each test.
    """
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Use our test database for testing
    db = TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        
    # Drop tables after test
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(test_db: Session) -> Generator:
    """
    Create a test client with the test database.
    """
    # Override the get_db dependency to use our test database
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create a test client
    with TestClient(app) as test_client:
        yield test_client
    
    # Reset the dependency override
    app.dependency_overrides = {} 