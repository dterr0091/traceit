from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, UploadFile, File
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
from ..models.db import get_db
from ..models.user import User, SearchHistory
from ..services.auth import get_current_active_user
from ..services.credit_service import CreditService
from ..services.router_service import RouterService
from ..services.vector_service import VectorService
from ..services.image_search_service import ImageSearchService
from pydantic import BaseModel, HttpUrl

router = APIRouter(
    prefix="/search",
    tags=["search"],
    responses={401: {"description": "Unauthorized"}},
)

class TextSearchRequest(BaseModel):
    query: str
    force_perplexity: bool = False

class UrlSearchRequest(BaseModel):
    url: HttpUrl
    force_perplexity: bool = False

class SearchResponse(BaseModel):
    job_id: str
    query_hash: str
    query_type: str
    perplexity_used: bool
    credits_used: int
    results: List[Dict[str, Any]]
    origins: List[Dict[str, Any]]
    confidence: float

@router.post("/text", response_model=SearchResponse)
async def search_text(
    request: TextSearchRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Search for the origin of text content"""
    # Determine query type and credit cost
    query_type = "light"  # URL or ≤500-char text
    credit_cost = CreditService.get_credit_cost(query_type)
    
    # Check if user has enough credits
    if not CreditService.use_credits(db, current_user.id, credit_cost):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient credits for this search"
        )
    
    # Create search history record
    search_record = SearchHistory(
        user_id=current_user.id,
        query_hash=VectorService.compute_content_hash(request.query),
        query_type=query_type,
        credits_used=credit_cost,
        perplexity_used=False  # Will be updated later if Perplexity is used
    )
    db.add(search_record)
    db.commit()
    db.refresh(search_record)
    
    # Perform search
    search_result = await RouterService.search(
        db=db,
        query=request.query,
        query_type=query_type,
        force_perplexity=request.force_perplexity
    )
    
    # Update search record if Perplexity was used
    if search_result["perplexity_used"]:
        search_record.perplexity_used = True
        db.commit()
    
    # Format response
    response = {
        "job_id": str(search_record.id),
        "query_hash": search_result["query_hash"],
        "query_type": query_type,
        "perplexity_used": search_result["perplexity_used"],
        "credits_used": credit_cost,
        "results": search_result["results"],
        "origins": search_result["origins"],
        "confidence": search_result["confidence"]
    }
    
    return response

@router.post("/url", response_model=SearchResponse)
async def search_url(
    request: UrlSearchRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Search for the origin of content at a URL"""
    # Determine query type and credit cost
    query_type = "light"  # URL or ≤500-char text
    credit_cost = CreditService.get_credit_cost(query_type)
    
    # Check if user has enough credits
    if not CreditService.use_credits(db, current_user.id, credit_cost):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient credits for this search"
        )
    
    # In a real implementation, we would fetch the content from the URL
    # For now, we'll just use the URL as the query
    query = str(request.url)
    
    # Create search history record
    search_record = SearchHistory(
        user_id=current_user.id,
        query_hash=VectorService.compute_content_hash(query),
        query_type=query_type,
        credits_used=credit_cost,
        perplexity_used=False  # Will be updated later if Perplexity is used
    )
    db.add(search_record)
    db.commit()
    db.refresh(search_record)
    
    # Perform search
    search_result = await RouterService.search(
        db=db,
        query=query,
        query_type=query_type,
        force_perplexity=request.force_perplexity
    )
    
    # Update search record if Perplexity was used
    if search_result["perplexity_used"]:
        search_record.perplexity_used = True
        db.commit()
    
    # Format response
    response = {
        "job_id": str(search_record.id),
        "query_hash": search_result["query_hash"],
        "query_type": query_type,
        "perplexity_used": search_result["perplexity_used"],
        "credits_used": credit_cost,
        "results": search_result["results"],
        "origins": search_result["origins"],
        "confidence": search_result["confidence"]
    }
    
    return response

@router.post("/image", response_model=SearchResponse)
async def search_image(
    image: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Search for the origin of an image"""
    # Determine query type and credit cost
    query_type = "heavy"  # Image or audio-only
    credit_cost = CreditService.get_credit_cost(query_type)
    
    # Check if user has enough credits
    if not CreditService.use_credits(db, current_user.id, credit_cost):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient credits for this search"
        )
    
    # Read the image data
    image_data = await image.read()
    
    # Create search history record
    image_hash = ImageSearchService.compute_image_hash(image_data)
    search_record = SearchHistory(
        user_id=current_user.id,
        query_hash=image_hash,
        query_type=query_type,
        credits_used=credit_cost,
        perplexity_used=False  # Images don't use Perplexity
    )
    db.add(search_record)
    db.commit()
    db.refresh(search_record)
    
    # Perform image search
    search_result = await ImageSearchService.search_image(db, image_data)
    
    # Format response
    response = {
        "job_id": str(search_record.id),
        "query_hash": search_result["query_hash"],
        "query_type": query_type,
        "perplexity_used": False,  # Images don't use Perplexity
        "credits_used": credit_cost,
        "results": search_result["results"],
        "origins": search_result["origins"],
        "confidence": search_result["confidence"]
    }
    
    return response

@router.get("/status/{job_id}")
async def get_search_status(
    job_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get status of a search job"""
    # Fetch search record
    search_record = db.query(SearchHistory).filter(
        SearchHistory.id == job_id,
        SearchHistory.user_id == current_user.id
    ).first()
    
    if not search_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Search job not found"
        )
    
    # In a more advanced implementation, this would check status for async jobs
    # For now, all searches are synchronous
    
    return {
        "job_id": job_id,
        "status": "completed",
        "query_type": search_record.query_type,
        "perplexity_used": search_record.perplexity_used,
        "credits_used": search_record.credits_used,
        "created_at": search_record.created_at.isoformat()
    }

@router.get("/tineye-batch/{batch_id}")
async def get_tineye_batch_status(
    batch_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get status of a TinEye batch
    Admin only
    """
    # Check if user is an admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    from ..services.tineye_service import TinEyeService
    
    result = await TinEyeService.check_batch_results(batch_id)
    return result

@router.post("/tineye-batch/run")
async def run_tineye_batch(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Manually run TinEye batch processing
    Admin only
    """
    # Check if user is an admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    from ..services.scheduler_service import SchedulerService
    
    result = await SchedulerService.force_run_tineye_batch()
    return result 