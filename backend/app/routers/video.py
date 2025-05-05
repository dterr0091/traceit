import os
import logging
import asyncio
import json
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
            
            # Start video processing in background
            background_tasks.add_task(
                video_pipeline.process_video_with_progress,
                file_path=temp_file,
                job_id=job_id
            )
        else:
            # Process from URL in background
            background_tasks.add_task(
                video_pipeline.process_video_with_progress,
                url=url,
                job_id=job_id
            )
        
        # Immediate response with job ID
        return {
            "job_id": job_id,
            "status": "processing",
            "message": "Video processing started"
        }
        
    except Exception as e:
        logger.error(f"Error in video processing endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing video: {str(e)}"
        )

@router.get("/progress/{job_id}")
async def video_progress_sse(
    job_id: str,
    user: Optional[Dict] = Depends(get_current_user)
):
    """
    Stream processing updates for a video job using Server-Sent Events.
    
    Args:
        job_id: The job ID to track
        user: Current authenticated user
        
    Returns:
        SSE stream with processing updates
    """
    
    async def event_generator():
        try:
            # Send initial connection established message
            yield f"data: {json.dumps({'status': 'connected', 'job_id': job_id})}\n\n"
            
            # Keep checking for progress updates until complete or error
            while True:
                # Get current job status from Redis
                job_status = await video_pipeline.redis_service.get_cache(f"video_progress:{job_id}")
                
                if not job_status:
                    # If no status found, check if there's a result already
                    result = await video_pipeline.redis_service.get_cache(f"video_result:{job_id}")
                    if result:
                        yield f"data: {json.dumps({'status': 'complete', 'result': result})}\n\n"
                        break
                    else:
                        yield f"data: {json.dumps({'status': 'pending', 'message': 'Waiting for job to start'})}\n\n"
                elif job_status.get("status") == "complete" or job_status.get("error"):
                    # Job is finished, send final update and close
                    yield f"data: {json.dumps(job_status)}\n\n"
                    break
                else:
                    # Send progress update
                    yield f"data: {json.dumps(job_status)}\n\n"
                
                # Wait before checking again
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error in SSE stream for job {job_id}: {str(e)}")
            yield f"data: {json.dumps({'status': 'error', 'message': str(e)})}\n\n"
        
        # Final message to close the connection
        yield f"data: {json.dumps({'status': 'closed'})}\n\n"
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'X-Accel-Buffering': 'no'  # For Nginx
        }
    )

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
        progress = await video_pipeline.redis_service.get_cache(f"video_progress:{job_id}")
        result = await video_pipeline.redis_service.get_cache(f"video_result:{job_id}")
        
        if result:
            return {
                "job_id": job_id,
                "status": "complete",
                "result": result
            }
        
        if progress:
            return progress
        
        return {
            "job_id": job_id,
            "status": "not_found",
            "message": "Job not found or expired"
        }
        
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