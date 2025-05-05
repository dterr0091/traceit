import os
import logging
import asyncio
import tempfile
import subprocess
from typing import List, Dict, Any, Optional, Tuple
import ffmpeg
import httpx
from uuid import uuid4
from pathlib import Path

from ..utils.file_utils import delete_file_if_exists

logger = logging.getLogger(__name__)

class FFmpegService:
    """
    Service for video processing using FFmpeg.
    Handles keyframe extraction and video analysis.
    """
    
    def __init__(self, temp_dir: Optional[str] = None):
        """
        Initialize the FFmpeg service.
        
        Args:
            temp_dir: Optional custom temp directory for extracted frames
        """
        self.temp_dir = temp_dir or os.path.join(tempfile.gettempdir(), "traceit_ffmpeg")
        
        # Ensure temp directory exists
        os.makedirs(self.temp_dir, exist_ok=True)
        
    async def download_video(self, url: str) -> Optional[str]:
        """
        Download a video from a URL.
        
        Args:
            url: URL to download from
            
        Returns:
            Path to downloaded file or None if failed
        """
        try:
            temp_file = os.path.join(self.temp_dir, f"{uuid4()}.mp4")
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("GET", url) as response:
                    if response.status_code != 200:
                        logger.error(f"Failed to download video: HTTP {response.status_code}")
                        return None
                    
                    with open(temp_file, "wb") as f:
                        async for chunk in response.aiter_bytes():
                            f.write(chunk)
            
            return temp_file
            
        except Exception as e:
            logger.error(f"Error downloading video: {str(e)}")
            return None
    
    async def extract_keyframes(self, 
                               video_path: str, 
                               frame_positions: List[float] = None,
                               frame_count: int = 3) -> List[str]:
        """
        Extract keyframes from a video.
        
        Args:
            video_path: Path to the video file
            frame_positions: List of positions (in seconds) to extract frames from
                             If not provided, will extract start, middle, and end frames
            frame_count: Number of frames to extract if positions not specified
            
        Returns:
            List of paths to extracted frame images
        """
        try:
            # Get video duration if frame positions not specified
            if not frame_positions:
                duration = await self.get_video_duration(video_path)
                if duration is None:
                    logger.error("Could not determine video duration")
                    return []
                
                # Calculate frame positions (start, middle, end)
                frame_positions = [
                    0,  # Start
                    duration / 2,  # Middle
                    max(0, duration - 0.5)  # End (avoid potential out-of-bounds)
                ]
            
            frame_paths = []
            
            # Extract each frame
            for i, position in enumerate(frame_positions):
                output_path = os.path.join(self.temp_dir, f"{Path(video_path).stem}_frame_{i}.jpg")
                
                # Construct FFmpeg command to extract the frame
                cmd = [
                    "ffmpeg",
                    "-y",  # Overwrite output files
                    "-ss", str(position),  # Seek to position
                    "-i", video_path,  # Input file
                    "-vframes", "1",  # Extract single frame
                    "-q:v", "2",  # High quality
                    output_path
                ]
                
                # Run FFmpeg to extract frame
                process = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                
                stdout, stderr = await process.communicate()
                
                if process.returncode != 0:
                    logger.error(f"FFmpeg error: {stderr.decode()}")
                    continue
                
                if os.path.exists(output_path):
                    frame_paths.append(output_path)
            
            return frame_paths
            
        except Exception as e:
            logger.error(f"Error extracting keyframes: {str(e)}")
            return []
    
    async def get_video_duration(self, video_path: str) -> Optional[float]:
        """
        Get the duration of a video in seconds.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Duration in seconds or None if failed
        """
        try:
            # Use ffprobe to get video duration
            probe = ffmpeg.probe(video_path)
            duration = float(probe['format']['duration'])
            return duration
            
        except Exception as e:
            logger.error(f"Error getting video duration: {str(e)}")
            return None
    
    async def get_video_metadata(self, video_path: str) -> Dict[str, Any]:
        """
        Get metadata about a video file.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Dict containing video metadata
        """
        try:
            probe = ffmpeg.probe(video_path)
            
            # Extract general format info
            format_info = probe['format']
            
            # Extract video stream info (first video stream)
            video_stream = next((s for s in probe['streams'] if s['codec_type'] == 'video'), None)
            
            # Extract audio stream info (first audio stream)
            audio_stream = next((s for s in probe['streams'] if s['codec_type'] == 'audio'), None)
            
            metadata = {
                "duration": float(format_info.get('duration', 0)),
                "size_bytes": int(format_info.get('size', 0)),
                "format": format_info.get('format_name', ''),
                "bitrate": int(format_info.get('bit_rate', 0)),
                "video": {
                    "codec": video_stream.get('codec_name', '') if video_stream else None,
                    "width": int(video_stream.get('width', 0)) if video_stream else None,
                    "height": int(video_stream.get('height', 0)) if video_stream else None,
                    "fps": eval(video_stream.get('avg_frame_rate', '0/1')) if video_stream else None,
                },
                "audio": {
                    "codec": audio_stream.get('codec_name', '') if audio_stream else None,
                    "channels": int(audio_stream.get('channels', 0)) if audio_stream else None,
                    "sample_rate": int(audio_stream.get('sample_rate', 0)) if audio_stream else None,
                },
                "has_audio": audio_stream is not None
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error getting video metadata: {str(e)}")
            return {
                "error": str(e),
                "duration": 0,
                "has_audio": False
            }
    
    async def extract_audio(self, video_path: str) -> Optional[str]:
        """
        Extract audio track from a video file.
        
        Args:
            video_path: Path to the video file
            
        Returns:
            Path to extracted audio file or None if failed
        """
        try:
            # Check if video has audio
            metadata = await self.get_video_metadata(video_path)
            if not metadata.get("has_audio", False):
                logger.warning(f"Video has no audio track: {video_path}")
                return None
            
            # Create output path for audio
            audio_path = os.path.join(self.temp_dir, f"{Path(video_path).stem}_audio.mp3")
            
            # Construct FFmpeg command to extract audio
            cmd = [
                "ffmpeg",
                "-y",  # Overwrite output files
                "-i", video_path,  # Input file
                "-vn",  # Disable video
                "-acodec", "libmp3lame",  # MP3 codec
                "-q:a", "4",  # Good quality (0-9, 0=best)
                audio_path
            ]
            
            # Run FFmpeg to extract audio
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                logger.error(f"FFmpeg error extracting audio: {stderr.decode()}")
                return None
            
            if os.path.exists(audio_path):
                return audio_path
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting audio from video: {str(e)}")
            return None
    
    def cleanup_temp_files(self, file_paths: List[str]):
        """
        Clean up temporary files.
        
        Args:
            file_paths: List of file paths to delete
        """
        for path in file_paths:
            delete_file_if_exists(path) 