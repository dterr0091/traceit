from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Any, Optional
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..services.lineage_service import LineageService
from ..services.auth_service import AuthService

router = APIRouter(
    prefix="/api/spread",
    tags=["spread"],
    responses={404: {"description": "Not found"}},
)

# Initialize services
lineage_service = LineageService()
auth_service = AuthService()
security = HTTPBearer()

@router.get("/{artifact_id}", response_model=Dict[str, Any])
async def get_spread_view(
    artifact_id: str,
    max_depth: int = Query(3, ge=1, le=5),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Get the spread view of content for a specific artifact.
    
    Shows how content has spread from its origin across the web.
    
    Args:
        artifact_id: ID of the artifact to get spread view for
        max_depth: Maximum depth of spread graph (1-5)
        
    Returns:
        Dict containing spread view data
    """
    # Verify token
    user = await auth_service.verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Get spread view
    result = await lineage_service.get_spread_view(artifact_id, max_depth)
    
    if result.get("status") == "error":
        raise HTTPException(
            status_code=500, 
            detail=f"Error getting spread view: {result.get('error', 'Unknown error')}"
        )
    
    return result

@router.post("/update", response_model=Dict[str, Any])
async def force_lineage_update(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Manually trigger a lineage graph update (admin only).
    
    This runs the nightly batch job that builds multi-hop relationships
    in the lineage graph.
    
    Returns:
        Dict containing update statistics
    """
    # Verify token and admin status
    user = await auth_service.verify_token(credentials.credentials)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    if not user.get("is_admin", False):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Run lineage update
    from ..services.scheduler_service import SchedulerService
    result = await SchedulerService.force_run_lineage_graph_update()
    
    if result.get("status") == "error":
        raise HTTPException(
            status_code=500, 
            detail=f"Error updating lineage graph: {result.get('error', 'Unknown error')}"
        )
    
    return result 