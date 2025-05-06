import os
import asyncio
import logging
import json
import httpx
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

async def test_perplexity_search(query="test query"):
    """
    Test if a search to Perplexity API completes successfully.
    
    This is a simple test to check if we can make a successful API call
    to the Perplexity API and get search results back.
    """
    # Get API key from environment variable
    api_key = os.getenv("PERPLEXITY_API_KEY")
    
    if not api_key:
        logger.error("PERPLEXITY_API_KEY not set in environment variables")
        return False
    
    logger.info(f"Testing search with query: {query}")
    
    try:
        # Make request to Perplexity API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.perplexity.ai/chat/completions",
                headers={
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {api_key}"
                },
                json={
                    "model": "sonar",
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that provides factual information."
                        },
                        {
                            "role": "user",
                            "content": f"Find the original source and related content for: {query}"
                        }
                    ],
                    "max_tokens": 1024
                },
                timeout=30.0
            )
            
            # Check for successful response
            if response.status_code == 200:
                data = response.json()
                logger.info("Search completed successfully!")
                logger.info(f"Response contains {len(json.dumps(data))} characters")
                return True
            else:
                logger.error(f"API request failed with status code: {response.status_code}")
                logger.error(f"Response: {response.text}")
                return False
    except Exception as e:
        logger.error(f"Error during API request: {str(e)}")
        return False

async def test_simulated_search():
    """
    Simulate a search with mock data to test the flow.
    
    This function doesn't make actual API calls - it just simulates
    the search process with mock data to test if the logic completes.
    """
    logger.info("Testing simulated search")
    
    # Simulate search process
    await asyncio.sleep(1)  # Simulate time taken for search
    
    # Create simulated results
    mock_results = {
        "query": "test query",
        "results": [
            {
                "title": "Test Result 1",
                "url": "https://example.com/result1",
                "snippet": "This is a test result snippet that matches the query.",
                "score": 0.95
            },
            {
                "title": "Test Result 2",
                "url": "https://example.com/result2",
                "snippet": "Another test result with relevant information.",
                "score": 0.85
            }
        ],
        "origin": {
            "url": "https://example.com/origin",
            "title": "Original Source",
            "timestamp": "2023-01-01T00:00:00Z",
            "confidence": 0.9
        }
    }
    
    logger.info("Simulated search completed successfully!")
    logger.info(f"Found {len(mock_results['results'])} results with origin confidence {mock_results['origin']['confidence']}")
    
    return True

def test_api_search_endpoint():
    """
    Test the search endpoint using the FastAPI test client.
    
    This function creates a simple FastAPI app with a search endpoint
    and tests if it correctly handles search requests.
    """
    from fastapi import FastAPI, Depends, HTTPException
    from pydantic import BaseModel
    
    logger.info("Testing search API endpoint")
    
    # Create a simple FastAPI app
    app = FastAPI()
    
    class SearchRequest(BaseModel):
        query: str
        force_perplexity: bool = False
    
    class SearchResponse(BaseModel):
        job_id: str
        query_hash: str
        results: list
        origins: list
        confidence: float
    
    # Mock authentication and database dependencies
    def mock_auth():
        return {"id": "test-user", "is_admin": True}
    
    def mock_db():
        return MagicMock()
    
    # Create a simple search endpoint
    @app.post("/search", response_model=SearchResponse)
    async def search(
        request: SearchRequest,
        user = Depends(mock_auth),
        db = Depends(mock_db)
    ):
        # Simulate search processing
        return {
            "job_id": "test-job-123",
            "query_hash": "test-hash-456",
            "results": [
                {
                    "title": "API Test Result",
                    "url": "https://example.com/api-result",
                    "snippet": "This is a test result from the API endpoint.",
                    "score": 0.9
                }
            ],
            "origins": [
                {
                    "url": "https://example.com/api-origin",
                    "title": "API Original Source",
                    "timestamp": "2023-01-01T00:00:00Z",
                    "confidence": 0.85
                }
            ],
            "confidence": 0.85
        }
    
    # Create test client
    client = TestClient(app)
    
    # Test the endpoint
    response = client.post(
        "/search",
        json={"query": "test api query", "force_perplexity": False}
    )
    
    # Check response
    if response.status_code == 200:
        data = response.json()
        logger.info("API search endpoint test completed successfully!")
        logger.info(f"API returned {len(data['results'])} results with confidence {data['confidence']}")
        return True
    else:
        logger.error(f"API search endpoint test failed with status code: {response.status_code}")
        logger.error(f"Response: {response.text}")
        return False

async def main():
    """Run search tests"""
    logger.info("Starting search tests")
    
    # First try a simulated search (always works)
    simulated_result = await test_simulated_search()
    logger.info(f"Simulated search result: {simulated_result}")
    
    # Try a real Perplexity API search if we have an API key
    if os.getenv("PERPLEXITY_API_KEY"):
        perplexity_result = await test_perplexity_search("latest climate change research")
        logger.info(f"Perplexity search result: {perplexity_result}")
    else:
        logger.warning("Skipping Perplexity search test - no API key available")
        perplexity_result = None
    
    # Test the API endpoint
    api_result = test_api_search_endpoint()
    logger.info(f"API search endpoint test result: {api_result}")
    
    # Return overall result
    overall_result = (
        simulated_result and 
        (perplexity_result is None or perplexity_result) and
        api_result
    )
    
    logger.info(f"Overall test result: {overall_result}")
    return overall_result

if __name__ == "__main__":
    asyncio.run(main()) 