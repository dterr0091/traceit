"""Tests for the video processor module."""
import pytest
from pathlib import Path
from typing import List
from services.video_processor import VideoProcessor, VideoProcessingError

@pytest.fixture
def video_processor() -> VideoProcessor:
    """Fixture to create a VideoProcessor instance."""
    return VideoProcessor()

@pytest.fixture
def sample_video_path(tmp_path: Path) -> Path:
    """Fixture to create a temporary video file for testing."""
    video_path = tmp_path / "test_video.mp4"
    # Create a minimal valid video file
    with open(video_path, "wb") as f:
        f.write(b"RIFF\x00\x00\x00\x00WEBM")
    return video_path

def test_extract_frames(video_processor: VideoProcessor, sample_video_path: Path, tmp_path: Path) -> None:
    """Test frame extraction from video."""
    output_dir = tmp_path / "frames"
    output_dir.mkdir()
    
    frames = video_processor.extract_frames(
        video_path=str(sample_video_path),
        output_dir=str(output_dir),
        interval=1  # Extract one frame per second
    )
    
    assert isinstance(frames, List)
    assert len(frames) > 0
    assert all(Path(frame).exists() for frame in frames)

def test_extract_subtitles(video_processor: VideoProcessor, sample_video_path: Path, tmp_path: Path) -> None:
    """Test subtitle extraction from video."""
    output_path = tmp_path / "subtitles.srt"
    
    subtitles = video_processor.extract_subtitles(
        video_path=str(sample_video_path),
        output_path=str(output_path)
    )
    
    assert isinstance(subtitles, str)
    assert Path(output_path).exists()

def test_invalid_video_path(video_processor: VideoProcessor) -> None:
    """Test handling of invalid video path."""
    with pytest.raises(VideoProcessingError):
        video_processor.extract_frames(
            video_path="nonexistent.mp4",
            output_dir="/tmp/frames",
            interval=1
        )

def test_invalid_output_dir(video_processor: VideoProcessor, sample_video_path: Path) -> None:
    """Test handling of invalid output directory."""
    with pytest.raises(VideoProcessingError):
        video_processor.extract_frames(
            video_path=str(sample_video_path),
            output_dir="/nonexistent/directory",
            interval=1
        ) 