import os
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse, JSONResponse
from uuid import uuid4

from ..services.video_pipeline_service import VideoPipelineService
from ..services.credit_service import CreditService
from ..services.auth import get_current_user
from ..utils.file_utils import save_upload_file_temp

router = APIRouter(
    prefix="/video",
    tags=["video"],
    responses={404: {"description": "Not found"}},
)

video_pipeline = VideoPipelineService()
credit_service = CreditService()

logger = logging.getLogger(__name__)

@router.post("/process")
async def process_video(
    background_tasks: BackgroundTasks,
    file: Optional[UploadFile] = File(None),
    url: Optional[str] = Form(None),
    job_id: Optional[str] = Form(None),
    user: Optional[Dict] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Process a video file or URL to identify its origin.
    
    Args:
        file: Optional video file upload
        url: Optional video URL
        job_id: Optional job ID for tracking
        user: Current authenticated user
        
    Returns:
        Processing result or job status
    """
    # Validate input
    if not file and not url:
        raise HTTPException(
            status_code=400, 
            detail="Either file or URL must be provided"
        )
    
    # Generate job ID if not provided
    job_id = job_id or str(uuid4())
    
    # Check if user has enough credits for video processing
    if user:
        # Video processing costs 8 credits
        credit_check = await credit_service.check_credits(user["id"], 8)
        if not credit_check["has_credits"]:
            raise HTTPException(
                status_code=402,
                detail=f"Insufficient credits. Video processing requires 8 credits, but you have {credit_check['balance']}."
            )
    
    temp_file = None
    
    try:
        # If file was uploaded, save it temporarily
        if file:
            temp_file = await save_upload_file_temp(file)
            
            # Start video processing
            result = await video_pipeline.process_video(
                file_path=temp_file,
                job_id=job_id
            )
        else:
            # Process from URL
            result = await video_pipeline.process_video(
                url=url,
                job_id=job_id
            )
        
        # Deduct credits if processing was successful and user is authenticated
        if user and not result.get("error") and not result.get("from_cache", False):
            await credit_service.deduct_credits(user["id"], 8, f"Video processing: {job_id}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in video processing endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing video: {str(e)}"
        )
    finally:
        # Clean up temp file in background to avoid blocking response
        if temp_file:
            background_tasks.add_task(os.unlink, temp_file)

@router.get("/status/{job_id}")
async def get_video_job_status(
    job_id: str,
    user: Optional[Dict] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Check the status of a video processing job.
    
    Args:
        job_id: The job ID to check
        user: Current authenticated user
        
    Returns:
        Current job status
    """
    try:
        # Use Redis to check job status
        result = await video_pipeline.redis_service.get(f"video_job:{job_id}")
        
        if not result:
            return {
                "job_id": job_id,
                "status": "not_found",
                "message": "Job not found or expired"
            }
        
        return result
        
    except Exception as e:
        logger.error(f"Error checking video job status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error checking job status: {str(e)}"
        )

@router.get("/extract-frames/{job_id}")
async def extract_frames_from_video(
    job_id: str,
    url: str,
    user: Optional[Dict] = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Extract keyframes from a video URL.
    This is a utility endpoint for debugging and testing.
    
    Args:
        job_id: The job ID to use
        url: Video URL to extract frames from
        user: Current authenticated user
        
    Returns:
        Paths to extracted frames
    """
    if not user or not user.get("is_admin", False):
        raise HTTPException(
            status_code=403,
            detail="Admin access required for this endpoint"
        )
    
    try:
        temp_file = None
        
        # Download the video
        temp_file = await video_pipeline.ffmpeg_service.download_video(url)
        if not temp_file:
            raise HTTPException(
                status_code=400,
                detail="Failed to download video from URL"
            )
        
        # Extract frames
        frame_paths = await video_pipeline.ffmpeg_service.extract_keyframes(temp_file)
        
        # Get frame data for response
        frames = []
        for i, path in enumerate(frame_paths):
            # You would typically upload these to storage
            # Here we're just returning the paths for testing
            frames.append({
                "index": i,
                "path": path
            })
        
        return {
            "job_id": job_id,
            "url": url,
            "frames": frames,
            "frame_count": len(frames)
        }
        
    except Exception as e:
        logger.error(f"Error extracting frames: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error extracting frames: {str(e)}"
        )
    finally:
        if temp_file:
            os.unlink(temp_file) 