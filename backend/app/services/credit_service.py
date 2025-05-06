from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.user import User, CreditBalance, CreditTransaction, SearchHistory
from fastapi import HTTPException, status, BackgroundTasks
import logging

class CreditService:
    @staticmethod
    def get_user_credits(db: Session, user_id: int) -> int:
        """Get current credit balance for a user"""
        credit_balance = db.query(CreditBalance).filter(CreditBalance.user_id == user_id).first()
        if not credit_balance:
            # Create default balance if not exists
            credit_balance = CreditBalance(user_id=user_id, balance=20, tier="free")
            db.add(credit_balance)
            db.commit()
            db.refresh(credit_balance)
        return credit_balance.balance
    
    @staticmethod
    def add_credits(db: Session, user_id: int, amount: int, transaction_type: str) -> int:
        """Add credits to a user's balance"""
        if amount <= 0:
            raise ValueError("Credit amount must be positive")
            
        credit_balance = db.query(CreditBalance).filter(CreditBalance.user_id == user_id).first()
        if not credit_balance:
            credit_balance = CreditBalance(user_id=user_id, balance=amount, tier="free")
            db.add(credit_balance)
        else:
            credit_balance.balance += amount
            
        # Record transaction
        transaction = CreditTransaction(
            user_id=user_id,
            amount=amount,
            transaction_type=transaction_type
        )
        db.add(transaction)
        db.commit()
        db.refresh(credit_balance)
        
        return credit_balance.balance
    
    @staticmethod
    async def use_credits(
        db: Session,
        user_id: int,
        amount: int,
        search_id: int = None,
        background_tasks: BackgroundTasks = None
    ) -> bool:
        """
        Use credits for a search operation
        
        Args:
            db: Database session
            user_id: User ID
            amount: Amount of credits to use
            search_id: ID of the search operation (if available)
            background_tasks: BackgroundTasks for notifications
            
        Returns:
            True if credits were successfully used, False if insufficient credits
            
        Raises:
            HTTPException if user doesn't exist
        """
        if amount <= 0:
            raise ValueError("Credit amount must be positive")
            
        credit_balance = db.query(CreditBalance).filter(CreditBalance.user_id == user_id).first()
        if not credit_balance:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found or credit balance not initialized"
            )
            
        # Check if user has enough credits
        if credit_balance.balance < amount:
            return False
            
        # Reduce balance
        credit_balance.balance -= amount
        
        # Record transaction
        transaction = CreditTransaction(
            user_id=user_id,
            amount=-amount,  # Negative amount for usage
            transaction_type="usage",
            search_id=search_id
        )
        db.add(transaction)
        db.commit()
        
        # Check if balance is low and send notification
        if background_tasks and credit_balance.balance <= 10:
            try:
                # Import here to avoid circular import
                from ..services.notification_service import NotificationService
                
                # Send low credits notification
                await NotificationService.notify_low_credits(
                    background_tasks=background_tasks,
                    db=db,
                    user_id=user_id,
                    current_balance=credit_balance.balance
                )
                
                logging.info(f"Low credit notification sent to user {user_id}")
            except Exception as e:
                logging.error(f"Failed to send low credit notification: {e}")
        
        return True
    
    @staticmethod
    def get_credit_cost(query_type: str) -> int:
        """
        Get credit cost based on query type
        
        Args:
            query_type: Type of query (light, heavy, video)
            
        Returns:
            Credit cost
        """
        cost_map = {
            "light": 1,   # URL or ≤500-char text
            "heavy": 3,   # Image or audio
            "video": 8    # Video content
        }
        return cost_map.get(query_type, 1)  # Default to 1 if unknown
    
    @staticmethod
    def get_transaction_history(db: Session, user_id: int, limit: int = 20, offset: int = 0):
        """Get credit transaction history for a user"""
        return (
            db.query(CreditTransaction)
            .filter(CreditTransaction.user_id == user_id)
            .order_by(CreditTransaction.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )
    
    @staticmethod
    def get_search_history(db: Session, user_id: int, limit: int = 20, offset: int = 0):
        """Get search history for a user"""
        return (
            db.query(SearchHistory)
            .filter(SearchHistory.user_id == user_id)
            .order_by(SearchHistory.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        ) 