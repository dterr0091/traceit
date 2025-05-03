import pytest
import os
from pathlib import Path
from services.openai_service import OpenAIService, SourceAnalysis
from unittest.mock import patch, MagicMock

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

@pytest.fixture
def openai_service():
    return OpenAIService()

@pytest.fixture
def sample_text():
    return "Breaking news: Major tech company announces new AI breakthrough"

@pytest.fixture
def sample_image_path(tmp_path):
    # Create a dummy image file
    image_path = tmp_path / "test.jpg"
    with open(image_path, "wb") as f:
        f.write(b"dummy image data")
    return str(image_path)

@pytest.fixture
def sample_video_path(tmp_path):
    # Create a dummy video file
    video_path = tmp_path / "test.mp4"
    with open(video_path, "wb") as f:
        f.write(b"dummy video data")
    return str(video_path)

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

@pytest.mark.asyncio
async def test_analyze_text(openai_service, sample_text):
    with patch("openai.ChatCompletion.acreate") as mock_create:
        mock_create.return_value = MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content="""Original Source: TechCrunch

Viral Points:
1. Twitter
2. LinkedIn
3. Reddit

Detailed analysis of the content's origin and spread.

Confidence Score: 0.85"""
                    )
                )
            ]
        )
        
        result = await openai_service.analyze_text(
            sample_text,
            "Twitter",
            {"timestamp": "2024-01-01T12:00:00Z"}
        )
        
        assert isinstance(result, SourceAnalysis)
        assert result.content_type == "text"
        assert result.original_source == "TechCrunch"
        assert len(result.viral_points) == 3
        assert result.confidence_score == 0.85

@pytest.mark.asyncio
async def test_analyze_image(openai_service, sample_image_path):
    with patch("openai.ChatCompletion.acreate") as mock_create:
        mock_create.return_value = MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content="""Original Source: Instagram

Viral Points:
1. Twitter
2. Facebook
3. Reddit

Detailed analysis of the image content.

Confidence Score: 0.9

Extracted Text: "New product launch #tech" """
                    )
                )
            ]
        )
        
        result = await openai_service.analyze_image(
            sample_image_path,
            "Instagram",
            {"timestamp": "2024-01-01T12:00:00Z"}
        )
        
        assert isinstance(result, SourceAnalysis)
        assert result.content_type == "image"
        assert result.original_source == "Instagram"
        assert len(result.viral_points) == 3
        assert result.confidence_score == 0.9
        assert "New product launch" in result.extracted_text

@pytest.mark.asyncio
async def test_analyze_video(openai_service, sample_video_path):
    with patch("services.video_processor.VideoProcessor.extract_key_frames") as mock_extract, \
         patch("openai.ChatCompletion.acreate") as mock_create:
        
        # Mock frame extraction
        mock_extract.return_value = ["frame1.jpg", "frame2.jpg"]
        
        # Mock OpenAI responses for each frame
        mock_create.side_effect = [
            MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content="""Original Source: YouTube

Viral Points:
1. Twitter
2. Instagram
3. TikTok

Frame 1 analysis.

Confidence Score: 0.8

Extracted Text: "Product demo" """
                        )
                    )
                ]
            ),
            MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content="""Original Source: YouTube

Viral Points:
1. Twitter
2. Instagram
3. TikTok

Frame 2 analysis.

Confidence Score: 0.85

Extracted Text: "Available now" """
                        )
                    )
                ]
            )
        ]
        
        result = await openai_service.analyze_video(
            sample_video_path,
            "YouTube",
            {"timestamp": "2024-01-01T12:00:00Z"}
        )
        
        assert isinstance(result, SourceAnalysis)
        assert result.content_type == "video"
        assert result.original_source == "YouTube"
        assert len(result.viral_points) == 3
        assert 0.8 <= result.confidence_score <= 0.85
        assert "Product demo" in result.extracted_text
        assert "Available now" in result.extracted_text

@pytest.mark.asyncio
async def test_analyze_source_text(openai_service, sample_text):
    with patch("openai.ChatCompletion.acreate") as mock_create:
        mock_create.return_value = MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content="""Original Source: TechCrunch

Viral Points:
1. Twitter
2. LinkedIn
3. Reddit

Detailed analysis.

Confidence Score: 0.85"""
                    )
                )
            ]
        )
        
        result = await openai_service.analyze_source(
            sample_text,
            "Twitter",
            {"timestamp": "2024-01-01T12:00:00Z"}
        )
        
        assert result.content_type == "text"

@pytest.mark.asyncio
async def test_analyze_source_image(openai_service, sample_image_path):
    with patch("openai.ChatCompletion.acreate") as mock_create:
        mock_create.return_value = MagicMock(
            choices=[
                MagicMock(
                    message=MagicMock(
                        content="""Original Source: Instagram

Viral Points:
1. Twitter
2. Facebook
3. Reddit

Detailed analysis.

Confidence Score: 0.9

Extracted Text: "New product launch" """
                    )
                )
            ]
        )
        
        result = await openai_service.analyze_source(
            sample_image_path,
            "Instagram",
            {"timestamp": "2024-01-01T12:00:00Z"}
        )
        
        assert result.content_type == "image"

@pytest.mark.asyncio
async def test_analyze_source_video(openai_service, sample_video_path):
    with patch("services.video_processor.VideoProcessor.extract_key_frames") as mock_extract, \
         patch("openai.ChatCompletion.acreate") as mock_create:
        
        mock_extract.return_value = ["frame1.jpg", "frame2.jpg"]
        mock_create.side_effect = [
            MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content="""Original Source: YouTube

Viral Points:
1. Twitter
2. Instagram
3. TikTok

Frame analysis.

Confidence Score: 0.8

Extracted Text: "Product demo" """
                        )
                    )
                ]
            ),
            MagicMock(
                choices=[
                    MagicMock(
                        message=MagicMock(
                            content="""Original Source: YouTube

Viral Points:
1. Twitter
2. Instagram
3. TikTok

Frame analysis.

Confidence Score: 0.85

Extracted Text: "Available now" """
                        )
                    )
                ]
            )
        ]
        
        result = await openai_service.analyze_source(
            sample_video_path,
            "YouTube",
            {"timestamp": "2024-01-01T12:00:00Z"}
        )
        
        assert result.content_type == "video"

@pytest.mark.asyncio
async def test_analyze_source_invalid_type(openai_service, tmp_path):
    invalid_file = tmp_path / "test.txt"
    with open(invalid_file, "w") as f:
        f.write("test content")
    
    with pytest.raises(ValueError, match="Unsupported content type"):
        await openai_service.analyze_source(
            str(invalid_file),
            "Unknown",
            {"timestamp": "2024-01-01T12:00:00Z"}
        ) 