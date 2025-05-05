import os
import logging
import tempfile
from typing import Optional, Dict, Any
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, HttpUrl

from ..services.audio_pipeline_service import AudioPipelineService
from ..services.credit_service import CreditService, verify_credits
from ..utils.file_utils import delete_file_if_exists
from ..services.auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/audio",
    tags=["audio"],
    responses={404: {"description": "Not found"}},
)

# Models
class AudioUrlRequest(BaseModel):
    url: HttpUrl
    job_id: Optional[str] = None

class AudioResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

# Service instance
audio_pipeline_service = AudioPipelineService()
credit_service = CreditService()

@router.post("/process/file", response_model=AudioResponse)
async def process_audio_file(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    job_id: Optional[str] = Form(None),
    user_id: str = Depends(get_current_user),
):
    """
    Process an audio file to find its origin.
    
    - **file**: Audio file to process
    - **job_id**: Optional job ID for bundled searches
    """
    # Check user credits
    credits_required = 3  # Heavy request (from spec)
    if not await verify_credits(user_id, credits_required):
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient credits. Required: {credits_required}"
        )
    
    # Create a temporary file to store the uploaded content
    temp_file = None
    try:
        # Save uploaded file to a temp file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1])
        temp_file_path = temp_file.name
        temp_file.close()
        
        # Write content to the temp file
        with open(temp_file_path, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Generate job ID if not provided
        job_id = job_id or str(uuid4())
        
        # Process the audio in the background
        background_tasks.add_task(
            process_audio_background,
            temp_file_path,
            job_id,
            user_id
        )
        
        # Deduct credits
        await credit_service.use_credits(user_id, credits_required)
        
        return AudioResponse(
            job_id=job_id,
            status="processing"
        )
        
    except Exception as e:
        logger.error(f"Error processing audio file: {str(e)}")
        if temp_file:
            delete_file_if_exists(temp_file.name)
        raise HTTPException(
            status_code=500,
            detail=f"Error processing audio file: {str(e)}"
        )

@router.post("/process/url", response_model=AudioResponse)
async def process_audio_url(
    request: AudioUrlRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user),
):
    """
    Process an audio file from a URL to find its origin.
    
    - **url**: URL to the audio file
    - **job_id**: Optional job ID for bundled searches
    """
    # Check user credits
    credits_required = 3  # Heavy request (from spec)
    if not await verify_credits(user_id, credits_required):
        raise HTTPException(
            status_code=402,
            detail=f"Insufficient credits. Required: {credits_required}"
        )
    
    try:
        # Generate job ID if not provided
        job_id = request.job_id or str(uuid4())
        
        # Process the audio in the background
        background_tasks.add_task(
            process_audio_url_background,
            request.url,
            job_id,
            user_id
        )
        
        # Deduct credits
        await credit_service.use_credits(user_id, credits_required)
        
        return AudioResponse(
            job_id=job_id,
            status="processing"
        )
        
    except Exception as e:
        logger.error(f"Error processing audio URL: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error processing audio URL: {str(e)}"
        )

@router.get("/status/{job_id}", response_model=AudioResponse)
async def get_audio_processing_status(
    job_id: str,
    user_id: str = Depends(get_current_user),
):
    """
    Get the status of an audio processing job.
    
    - **job_id**: The job ID to check
    """
    try:
        # Check Redis for job status
        result = await audio_pipeline_service.redis_service.get(f"job:{job_id}")
        
        if not result:
            return AudioResponse(
                job_id=job_id,
                status="not_found"
            )
            
        return AudioResponse(
            job_id=job_id,
            status=result.get("status", "unknown"),
            result=result.get("result"),
            error=result.get("error")
        )
        
    except Exception as e:
        logger.error(f"Error getting audio job status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting audio job status: {str(e)}"
        )

# Background processing functions
async def process_audio_background(file_path: str, job_id: str, user_id: str):
    """Background task to process an audio file."""
    try:
        # Update job status to processing
        await audio_pipeline_service.redis_service.set(
            f"job:{job_id}",
            {"status": "processing"}
        )
        
        # Process the audio
        result = await audio_pipeline_service.process_audio(
            file_path=file_path,
            job_id=job_id
        )
        
        # Update job status with result
        await audio_pipeline_service.redis_service.set(
            f"job:{job_id}",
            {
                "status": "completed",
                "result": result
            },
            expire_seconds=60*60*24*7  # 7 days
        )
        
    except Exception as e:
        logger.error(f"Error in audio background processing: {str(e)}")
        # Update job status with error
        await audio_pipeline_service.redis_service.set(
            f"job:{job_id}",
            {
                "status": "error",
                "error": str(e)
            },
            expire_seconds=60*60*24  # 1 day
        )
    finally:
        # Clean up temp file
        delete_file_if_exists(file_path)

async def process_audio_url_background(url: str, job_id: str, user_id: str):
    """Background task to process an audio file from a URL."""
    try:
        # Update job status to processing
        await audio_pipeline_service.redis_service.set(
            f"job:{job_id}",
            {"status": "processing"}
        )
        
        # Process the audio
        result = await audio_pipeline_service.process_audio(
            url=url,
            job_id=job_id
        )
        
        # Update job status with result
        await audio_pipeline_service.redis_service.set(
            f"job:{job_id}",
            {
                "status": "completed",
                "result": result
            },
            expire_seconds=60*60*24*7  # 7 days
        )
        
    except Exception as e:
        logger.error(f"Error in audio URL background processing: {str(e)}")
        # Update job status with error
        await audio_pipeline_service.redis_service.set(
            f"job:{job_id}",
            {
                "status": "error",
                "error": str(e)
            },
            expire_seconds=60*60*24  # 1 day
        ) 