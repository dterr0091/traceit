from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.user import User
from app.core.auth import get_current_user
from app.schemas.search import SearchRequest, SearchResponse
from app.services.search_service import SearchService

router = APIRouter()


@router.post("/", response_model=SearchResponse)
async def search_content(
    request: SearchRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Search for the origin of content (URL, text, image, audio, video)
    """
    search_service = SearchService(db)
    
    # Check if user has enough credits
    if not search_service.has_sufficient_credits(current_user.id, request):
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Insufficient credits for this search",
        )
    
    # Process search request
    search_result = await search_service.process_search(current_user.id, request)
    
    return search_result 