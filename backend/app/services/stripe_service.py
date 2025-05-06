import stripe
import os
import logging
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from ..models.user import User, CreditBalance, CreditTransaction
from typing import Dict, Any, Optional

# Initialize stripe with API key
stripe.api_key = os.getenv("STRIPE_API_KEY")
if not stripe.api_key:
    logging.warning("STRIPE_API_KEY not set. Stripe functionality will be disabled.")

class StripeService:
    @staticmethod
    def create_customer(db: Session, user_id: int, email: str) -> str:
        """
        Create a Stripe customer for a user
        
        Args:
            db: Database session
            user_id: User ID
            email: User email
            
        Returns:
            Stripe customer ID
        """
        try:
            # Create customer in Stripe
            customer = stripe.Customer.create(
                email=email,
                metadata={"user_id": str(user_id)}
            )
            
            # Update user in database
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Add stripe_customer_id to user model if it doesn't exist
            if not hasattr(user, 'stripe_customer_id'):
                logging.warning("stripe_customer_id field not found in User model. Please add this field.")
            else:
                user.stripe_customer_id = customer.id
                db.commit()
            
            return customer.id
        except stripe.error.StripeError as e:
            logging.error(f"Stripe error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {e}"
            )
    
    @staticmethod
    def create_subscription(db: Session, user_id: int, price_id: str, customer_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a subscription for a user
        
        Args:
            db: Database session
            user_id: User ID
            price_id: Stripe price ID
            customer_id: Optional Stripe customer ID
            
        Returns:
            Subscription details
        """
        try:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )
            
            # Get or create customer ID
            if not customer_id:
                if hasattr(user, 'stripe_customer_id') and user.stripe_customer_id:
                    customer_id = user.stripe_customer_id
                else:
                    customer_id = StripeService.create_customer(db, user_id, user.email)
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{"price": price_id}],
                metadata={"user_id": str(user_id)}
            )
            
            # Update user tier based on price ID
            if price_id.endswith("premium"):
                new_tier = "premium"
            elif price_id.endswith("enterprise"):
                new_tier = "enterprise"
            else:
                new_tier = "free"
            
            credit_balance = db.query(CreditBalance).filter(CreditBalance.user_id == user_id).first()
            if credit_balance:
                credit_balance.tier = new_tier
                db.commit()
            
            return {
                "subscription_id": subscription.id,
                "status": subscription.status,
                "current_period_end": subscription.current_period_end,
                "tier": new_tier
            }
        except stripe.error.StripeError as e:
            logging.error(f"Stripe error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {e}"
            )
    
    @staticmethod
    def cancel_subscription(subscription_id: str) -> Dict[str, Any]:
        """
        Cancel a subscription
        
        Args:
            subscription_id: Stripe subscription ID
            
        Returns:
            Cancellation details
        """
        try:
            subscription = stripe.Subscription.delete(subscription_id)
            return {
                "subscription_id": subscription_id,
                "status": subscription.status
            }
        except stripe.error.StripeError as e:
            logging.error(f"Stripe error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stripe error: {e}"
            )
    
    @staticmethod
    def handle_webhook(payload: Dict[str, Any], signature: str, webhook_secret: str, db: Session) -> Dict[str, Any]:
        """
        Handle Stripe webhook events
        
        Args:
            payload: Webhook payload
            signature: Stripe signature
            webhook_secret: Webhook secret
            db: Database session
            
        Returns:
            Response details
        """
        try:
            event = stripe.Webhook.construct_event(
                payload, signature, webhook_secret
            )
            
            # Handle different event types
            if event.type == 'invoice.payment_succeeded':
                return StripeService._handle_payment_succeeded(event, db)
            elif event.type == 'customer.subscription.updated':
                return StripeService._handle_subscription_updated(event, db)
            elif event.type == 'customer.subscription.deleted':
                return StripeService._handle_subscription_deleted(event, db)
            
            # Return default response for unhandled events
            return {"status": "success", "message": f"Unhandled event: {event.type}"}
        
        except (stripe.error.SignatureVerificationError, ValueError) as e:
            logging.error(f"Webhook error: {e}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Webhook error: {e}"
            )
    
    @staticmethod
    def _handle_payment_succeeded(event: stripe.Event, db: Session) -> Dict[str, Any]:
        """Handle invoice.payment_succeeded event"""
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
                except:
                    pass
        
        if user_id:
            # Convert to integer if found
            try:
                user_id = int(user_id)
            except:
                user_id = None
        
        if user_id:
            # Add credits based on the plan
            credit_amounts = {
                "premium": 100,
                "enterprise": 300,
                "free": 20
            }
            
            user = db.query(User).filter(User.id == user_id).first()
            credit_balance = db.query(CreditBalance).filter(CreditBalance.user_id == user_id).first()
            
            if credit_balance:
                tier = credit_balance.tier
                credits_to_add = credit_amounts.get(tier, 20)
                
                # Create transaction
                transaction = CreditTransaction(
                    user_id=user_id,
                    amount=credits_to_add,
                    transaction_type="subscription_renewal"
                )
                db.add(transaction)
                
                # Update balance
                credit_balance.balance += credits_to_add
                db.commit()
        
        return {"status": "success", "message": "Payment processed"}
    
    @staticmethod
    def _handle_subscription_updated(event: stripe.Event, db: Session) -> Dict[str, Any]:
        """Handle customer.subscription.updated event"""
        subscription = event.data.object
        user_id = subscription.metadata.get('user_id')
        
        if user_id:
            # Update tier based on subscription
            items = subscription.get('items', {}).get('data', [])
            if items:
                price_id = items[0].get('price', {}).get('id')
                if price_id:
                    if 'premium' in price_id:
                        new_tier = "premium"
                    elif 'enterprise' in price_id:
                        new_tier = "enterprise"
                    else:
                        new_tier = "free"
                    
                    # Update user tier
                    credit_balance = db.query(CreditBalance).filter(CreditBalance.user_id == int(user_id)).first()
                    if credit_balance:
                        credit_balance.tier = new_tier
                        db.commit()
        
        return {"status": "success", "message": "Subscription updated"}
    
    @staticmethod
    def _handle_subscription_deleted(event: stripe.Event, db: Session) -> Dict[str, Any]:
        """Handle customer.subscription.deleted event"""
        subscription = event.data.object
        user_id = subscription.metadata.get('user_id')
        
        if user_id:
            # Downgrade to free tier
            credit_balance = db.query(CreditBalance).filter(CreditBalance.user_id == int(user_id)).first()
            if credit_balance:
                credit_balance.tier = "free"
                db.commit()
        
        return {"status": "success", "message": "Subscription cancelled"} 