import pytest
from unittest.mock import AsyncMock, patch
from services.openai_service import OpenAIService, SourceAnalysis

@pytest.fixture
def mock_openai_response():
    return {
        "choices": [{
            "message": {
                "content": """
                Original Source: https://example.com/original

                Viral Points:
                1. Twitter post by @user1
                2. Reddit thread in r/news
                3. Facebook share by Page X

                Explanation:
                The content appears to have originated from example.com based on timestamp analysis and content similarity. It gained traction through social media shares, particularly on Twitter and Reddit.

                Confidence Score: 0.85
                """
            }
        }]
    }

@pytest.fixture
def mock_credibility_response():
    return {
        "choices": [{
            "message": {
                "content": """
                Credibility Score: 0.8

                Key Factors:
                - Established domain
                - Author credentials
                - Multiple citations
                - Fact-checking history

                Potential Biases:
                - Corporate ownership
                - Political leanings
                - Advertising relationships

                Verification Recommendations:
                - Check fact-checking sites
                - Review author history
                - Compare with other sources
                - Examine update history
                """
            }
        }]
    }

@pytest.mark.asyncio
async def test_analyze_source(mock_openai_response):
    with patch('openai.ChatCompletion.acreate', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_openai_response
        
        service = OpenAIService()
        result = await service.analyze_source(
            content="Test content",
            platform="twitter",
            metadata={"timestamp": "2024-01-01"}
        )
        
        assert isinstance(result, SourceAnalysis)
        assert result.original_source == "https://example.com/original"
        assert len(result.viral_points) == 3
        assert result.confidence_score == 0.85
        assert "timestamp analysis" in result.explanation.lower()

@pytest.mark.asyncio
async def test_evaluate_source_credibility(mock_credibility_response):
    with patch('openai.ChatCompletion.acreate', new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_credibility_response
        
        service = OpenAIService()
        result = await service.evaluate_source_credibility(
            source_url="https://example.com",
            content="Test content"
        )
        
        assert isinstance(result, dict)
        assert result["credibility_score"] == 0.8
        assert len(result["key_factors"]) == 4
        assert len(result["biases"]) == 3
        assert len(result["verification_recommendations"]) == 4

@pytest.mark.asyncio
async def test_analyze_source_error_handling():
    with patch('openai.ChatCompletion.acreate', new_callable=AsyncMock) as mock_create:
        mock_create.side_effect = Exception("API Error")
        
        service = OpenAIService()
        result = await service.analyze_source(
            content="Test content",
            platform="twitter",
            metadata={}
        )
        
        assert result.original_source == "Unknown"
        assert result.confidence_score == 0.0
        assert result.explanation == "Analysis failed due to an error"
        assert len(result.viral_points) == 0 