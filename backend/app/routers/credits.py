from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.db import get_db
from ..models.user import User, CreditTransaction, SearchHistory
from ..services.auth import get_current_active_user
from ..services.credit_service import CreditService
from pydantic import BaseModel

router = APIRouter(
    prefix="/credits",
    tags=["credits"],
    responses={401: {"description": "Unauthorized"}},
)

class CreditTransactionResponse(BaseModel):
    id: int
    amount: int
    transaction_type: str
    created_at: str
    search_id: Optional[int] = None

class SearchHistoryResponse(BaseModel):
    id: int
    query_hash: str
    query_type: str
    credits_used: int
    perplexity_used: bool
    created_at: str

@router.get("/balance")
def get_credit_balance(current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """Get user's current credit balance"""
    balance = CreditService.get_user_credits(db, current_user.id)
    return {"balance": balance, "tier": current_user.credit_balance.tier}

@router.post("/add")
def add_credits(
    amount: int,
    transaction_type: str = "purchase",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Add credits to user's balance (admin or via purchase)"""
    # In a real app, validate purchase or apply admin privileges here
    try:
        new_balance = CreditService.add_credits(db, current_user.id, amount, transaction_type)
        return {"success": True, "new_balance": new_balance}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/transactions", response_model=List[CreditTransactionResponse])
def get_transaction_history(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's credit transaction history"""
    transactions = CreditService.get_transaction_history(db, current_user.id, limit, offset)
    
    # Format response
    result = []
    for tx in transactions:
        result.append({
            "id": tx.id,
            "amount": tx.amount,
            "transaction_type": tx.transaction_type,
            "created_at": tx.created_at.isoformat(),
            "search_id": tx.search_id
        })
    
    return result

@router.get("/searches", response_model=List[SearchHistoryResponse])
def get_search_history(
    limit: int = 20,
    offset: int = 0,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's search history"""
    searches = CreditService.get_search_history(db, current_user.id, limit, offset)
    
    # Format response
    result = []
    for search in searches:
        result.append({
            "id": search.id,
            "query_hash": search.query_hash,
            "query_type": search.query_type,
            "credits_used": search.credits_used,
            "perplexity_used": search.perplexity_used,
            "created_at": search.created_at.isoformat()
        })
    
    return result 