import os
import logging
import tempfile
import uuid
import shutil
from pathlib import Path
from typing import Optional, BinaryIO
from fastapi import UploadFile
import boto3
from botocore.exceptions import ClientError

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
        import ffmpeg
        probe = ffmpeg.probe(file_path)
        duration = float(probe['format']['duration'])
        return duration
        
    except Exception as e:
        logger.error(f"Error getting audio duration for {file_path}: {str(e)}")
        return None 

async def save_upload_file_temp(upload_file: UploadFile) -> str:
    """
    Save an uploaded file to a temporary file.
    
    Args:
        upload_file: FastAPI UploadFile
        
    Returns:
        Path to the temporary file
    """
    try:
        # Generate a unique temporary file path
        suffix = Path(upload_file.filename).suffix if upload_file.filename else ''
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            # Write file contents to the temp file
            shutil.copyfileobj(upload_file.file, tmp)
            tmp_path = tmp.name
        
        # Reset file position after reading
        await upload_file.seek(0)
        
        return tmp_path
    except Exception as e:
        logger.error(f"Error saving uploaded file: {str(e)}")
        raise e

async def upload_to_storage(file_path: str, bucket_name: str = None) -> Optional[str]:
    """
    Upload a file to cloud storage (S3 or compatible).
    
    Args:
        file_path: Path to the local file
        bucket_name: Optional bucket name (defaults to env var)
        
    Returns:
        Public URL of the uploaded file, or None if failed
    """
    try:
        # Get bucket name from environment or parameter
        bucket = bucket_name or os.getenv("S3_BUCKET_NAME")
        if not bucket:
            logger.error("No S3 bucket specified - check environment variables")
            return None
        
        # Initialize S3 client
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION"),
            endpoint_url=os.getenv("S3_ENDPOINT_URL")  # For non-AWS S3 compatible services
        )
        
        # Generate unique object name
        file_extension = get_file_extension(file_path)
        object_name = f"uploads/{uuid.uuid4()}{file_extension}"
        
        # Upload the file
        s3_client.upload_file(
            file_path, 
            bucket, 
            object_name,
            ExtraArgs={'ACL': 'public-read'}  # Make file publicly accessible
        )
        
        # Generate and return the public URL
        if os.getenv("S3_ENDPOINT_URL"):
            # For custom S3-compatible storage
            url = f"{os.getenv('S3_ENDPOINT_URL')}/{bucket}/{object_name}"
        else:
            # For AWS S3
            region = os.getenv("AWS_REGION", "us-east-1")
            url = f"https://{bucket}.s3.{region}.amazonaws.com/{object_name}"
            
        return url
        
    except ClientError as e:
        logger.error(f"S3 upload error: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error uploading file to storage: {str(e)}")
        return None 