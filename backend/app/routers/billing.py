from fastapi import APIRouter, Depends, HTTPException, status, Request, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional, List
import stripe
import os
import json
import logging

from ..models.db import get_db
from ..models.user import User, CreditBalance
from ..services.auth import get_current_active_user
from ..services.stripe_service import StripeService
from ..services.notification_service import NotificationService
from pydantic import BaseModel

router = APIRouter(
    prefix="/billing",
    tags=["billing"],
    responses={401: {"description": "Unauthorized"}},
)

class SubscriptionRequest(BaseModel):
    price_id: str

class SubscriptionResponse(BaseModel):
    subscription_id: str
    status: str
    current_period_end: int
    tier: str

class CreateCheckoutSessionRequest(BaseModel):
    price_id: str
    success_url: str
    cancel_url: str

class CreateCheckoutSessionResponse(BaseModel):
    checkout_url: str

@router.post("/subscribe", response_model=SubscriptionResponse)
async def create_subscription(
    subscription: SubscriptionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a subscription for the current user
    
    Args:
        subscription: Subscription details
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Subscription details
    """
    try:
        result = StripeService.create_subscription(
            db=db,
            user_id=current_user.id,
            price_id=subscription.price_id
        )
        return result
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to create subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create subscription: {str(e)}"
        )

@router.post("/create-checkout-session", response_model=CreateCheckoutSessionResponse)
async def create_checkout_session(
    request: CreateCheckoutSessionRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Create a Stripe checkout session
    
    Args:
        request: Checkout session details
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Checkout URL
    """
    try:
        # Get or create Stripe customer
        customer_id = None
        
        # Check if user has a Stripe customer ID
        if hasattr(current_user, 'stripe_customer_id') and current_user.stripe_customer_id:
            customer_id = current_user.stripe_customer_id
        else:
            # Create a new customer
            customer_id = StripeService.create_customer(
                db=db,
                user_id=current_user.id,
                email=current_user.email
            )
        
        # Create checkout session
        checkout_session = stripe.checkout.Session.create(
            customer=customer_id,
            payment_method_types=['card'],
            line_items=[{
                'price': request.price_id,
                'quantity': 1,
            }],
            mode='subscription',
            success_url=request.success_url,
            cancel_url=request.cancel_url,
            metadata={
                'user_id': str(current_user.id)
            }
        )
        
        return {"checkout_url": checkout_session.url}
    except stripe.error.StripeError as e:
        logging.error(f"Stripe error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )
    except Exception as e:
        logging.error(f"Failed to create checkout session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}"
        )

@router.post("/cancel-subscription/{subscription_id}")
async def cancel_subscription(
    subscription_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Cancel a subscription
    
    Args:
        subscription_id: Stripe subscription ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Cancellation status
    """
    try:
        result = StripeService.cancel_subscription(subscription_id)
        
        # Update user's tier to free
        credit_balance = db.query(CreditBalance).filter(CreditBalance.user_id == current_user.id).first()
        if credit_balance:
            credit_balance.tier = "free"
            db.commit()
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to cancel subscription: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )

@router.post("/webhook")
async def webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Handle Stripe webhook events
    
    Args:
        request: FastAPI request
        background_tasks: FastAPI background tasks
        db: Database session
        
    Returns:
        Webhook processing status
    """
    # Get webhook secret from environment
    webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET")
    if not webhook_secret:
        logging.error("STRIPE_WEBHOOK_SECRET not set")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Webhook secret not configured"
        )
    
    # Get request body
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    if not sig_header:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature"
        )
    
    try:
        # Process webhook
        result = StripeService.handle_webhook(
            payload=payload,
            signature=sig_header,
            webhook_secret=webhook_secret,
            db=db
        )
        
        # Check if we need to send notifications
        event = stripe.Event.construct_from(
            json.loads(payload),
            stripe.api_key
        )
        
        # Handle payment success notification
        if event.type == 'invoice.payment_succeeded':
            await _handle_payment_success_notification(event, db, background_tasks)
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to process webhook: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook error: {str(e)}"
        )

async def _handle_payment_success_notification(
    event: stripe.Event,
    db: Session,
    background_tasks: BackgroundTasks
):
    """Send notification for successful payment"""
    try:
        invoice = event.data.object
        
        # Get user from customer ID
        user_id = None
        customer_id = invoice.get('customer')
        if customer_id:
            # Find user with this customer ID
            user = db.query(User).filter_by(stripe_customer_id=customer_id).first()
            if user:
                user_id = user.id
        
        if not user_id:
            # Try to get from metadata
            subscription_id = invoice.get('subscription')
            if subscription_id:
                try:
                    subscription = stripe.Subscription.retrieve(subscription_id)
                    user_id = subscription.metadata.get('user_id')
                    if user_id:
                        user_id = int(user_id)
                except:
                    pass
        
        if user_id:
            # Get credit details
            credit_balance = db.query(CreditBalance).filter(CreditBalance.user_id == user_id).first()
            if credit_balance:
                tier = credit_balance.tier
                credits_added = {
                    "premium": 100,
                    "enterprise": 300,
                    "free": 20
                }.get(tier, 20)
                
                # Send notification
                await NotificationService.notify_subscription_renewal(
                    background_tasks=background_tasks,
                    db=db,
                    user_id=user_id,
                    credits_added=credits_added,
                    new_balance=credit_balance.balance,
                    tier=tier
                )
    except Exception as e:
        logging.error(f"Failed to send payment notification: {e}")
        # Don't raise the exception to avoid failing the webhook 