"""Video processing module for extracting frames and subtitles from videos."""
import os
import logging
from pathlib import Path
from typing import List
import ffmpeg
from pydantic import BaseModel, Field

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoProcessingError(Exception):
    """Custom exception for video processing errors."""
    pass

class VideoProcessor:
    """Handles video processing operations using ffmpeg."""
    
    def __init__(self) -> None:
        """Initialize the video processor."""
        self._validate_ffmpeg_installation()
    
    def _validate_ffmpeg_installation(self) -> None:
        """Validate that ffmpeg is installed and accessible."""
        try:
            ffmpeg.probe('dummy')
        except ffmpeg.Error:
            # Expected error since we're probing a dummy file
            pass
        except Exception as e:
            raise VideoProcessingError(f"FFmpeg not properly installed: {str(e)}")
    
    def extract_frames(
        self,
        video_path: str,
        output_dir: str,
        interval: int = 1,
        format: str = "jpg"
    ) -> List[str]:
        """
        Extract frames from a video at specified intervals.
        
        Args:
            video_path: Path to the input video file
            output_dir: Directory to save extracted frames
            interval: Interval in seconds between extracted frames
            format: Output image format (default: jpg)
            
        Returns:
            List of paths to extracted frame images
            
        Raises:
            VideoProcessingError: If video processing fails
        """
        try:
            # Validate input paths
            if not os.path.exists(video_path):
                raise VideoProcessingError(f"Video file not found: {video_path}")
            
            output_dir_path = Path(output_dir)
            output_dir_path.mkdir(parents=True, exist_ok=True)
            
            # Get video duration
            probe = ffmpeg.probe(video_path)
            duration = float(probe['format']['duration'])
            
            # Extract frames
            frame_paths = []
            for i in range(0, int(duration), interval):
                output_path = output_dir_path / f"frame_{i:04d}.{format}"
                try:
                    (
                        ffmpeg
                        .input(video_path)
                        .filter('select', f'eq(n,{i})')
                        .output(str(output_path), vframes=1)
                        .overwrite_output()
                        .run(capture_stdout=True, capture_stderr=True)
                    )
                    frame_paths.append(str(output_path))
                except ffmpeg.Error as e:
                    logger.warning(f"Failed to extract frame at {i}s: {str(e)}")
            
            if not frame_paths:
                raise VideoProcessingError("No frames were extracted from the video")
            
            return frame_paths
            
        except ffmpeg.Error as e:
            raise VideoProcessingError(f"FFmpeg error: {str(e)}")
        except Exception as e:
            raise VideoProcessingError(f"Unexpected error: {str(e)}")
    
    def extract_subtitles(
        self,
        video_path: str,
        output_path: str,
        language: str = "eng"
    ) -> str:
        """
        Extract subtitles from a video using ffmpeg.
        
        Args:
            video_path: Path to the input video file
            output_path: Path to save the extracted subtitles
            language: Language code for subtitle extraction (default: eng)
            
        Returns:
            Path to the extracted subtitle file
            
        Raises:
            VideoProcessingError: If subtitle extraction fails
        """
        try:
            # Validate input path
            if not os.path.exists(video_path):
                raise VideoProcessingError(f"Video file not found: {video_path}")
            
            # Extract subtitles
            (
                ffmpeg
                .input(video_path)
                .output(output_path, map=f'0:s:m:language:{language}')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            
            if not os.path.exists(output_path):
                raise VideoProcessingError("Subtitle extraction failed - no output file created")
            
            return output_path
            
        except ffmpeg.Error as e:
            raise VideoProcessingError(f"FFmpeg error: {str(e)}")
        except Exception as e:
            raise VideoProcessingError(f"Unexpected error: {str(e)}") 