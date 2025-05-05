import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

def delete_file_if_exists(file_path: str) -> bool:
    """
    Delete a file if it exists.
    
    Args:
        file_path: Path to the file to delete
        
    Returns:
        True if file was deleted or didn't exist, False if deletion failed
    """
    if not file_path:
        return True
        
    try:
        path = Path(file_path)
        if path.is_file():
            path.unlink()
            logger.debug(f"Deleted file: {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {str(e)}")
        return False

def ensure_directory_exists(directory_path: str) -> bool:
    """
    Ensure that a directory exists, creating it if necessary.
    
    Args:
        directory_path: Path to the directory
        
    Returns:
        True if directory exists or was created, False if creation failed
    """
    try:
        path = Path(directory_path)
        path.mkdir(parents=True, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Error creating directory {directory_path}: {str(e)}")
        return False

def get_file_extension(file_path: str) -> str:
    """
    Get the extension of a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        File extension (lowercase) including the dot, or empty string if no extension
    """
    return os.path.splitext(file_path)[1].lower()

def get_audio_file_duration(file_path: str) -> Optional[float]:
    """
    Get the duration of an audio file in seconds.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        Duration in seconds, or None if failed
    """
    try:
        # This is a placeholder - in a real implementation, you would use a library
        # like pydub, librosa, or ffmpeg-python to get the duration
        
        # Example with ffmpeg-python (would need to add to requirements.txt):
        # import ffmpeg
        # probe = ffmpeg.probe(file_path)
        # duration = float(probe['format']['duration'])
        # return duration
        
        logger.warning("get_audio_file_duration is a placeholder - implement with audio library")
        return None
    except Exception as e:
        logger.error(f"Error getting audio duration for {file_path}: {str(e)}")
        return None 