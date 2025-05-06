import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
from fastapi import BackgroundTasks
from ..models.user import User

class NotificationService:
    # Email configuration
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "no-reply@trace.app")
    
    # Email templates path
    TEMPLATES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
    
    @staticmethod
    async def send_email_notification(
        background_tasks: BackgroundTasks,
        recipient_email: str,
        subject: str,
        template_name: str,
        template_data: Dict[str, Any]
    ):
        """
        Send an email notification in the background
        
        Args:
            background_tasks: FastAPI BackgroundTasks
            recipient_email: Email recipient
            subject: Email subject
            template_name: Template file name
            template_data: Template data
        """
        background_tasks.add_task(
            NotificationService._send_email,
            recipient_email,
            subject,
            template_name,
            template_data
        )
    
    @staticmethod
    def _send_email(
        recipient_email: str,
        subject: str,
        template_name: str,
        template_data: Dict[str, Any]
    ):
        """
        Send an email notification
        
        Args:
            recipient_email: Email recipient
            subject: Email subject
            template_name: Template file name
            template_data: Template data
        """
        if not NotificationService.SMTP_USERNAME or not NotificationService.SMTP_PASSWORD:
            logging.warning("SMTP credentials not configured. Email not sent.")
            return
        
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = NotificationService.SENDER_EMAIL
            message["To"] = recipient_email
            
            # Load template and substitute variables
            html_content = NotificationService._load_template(template_name, template_data)
            
            # Attach HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)
            
            # Send email
            with smtplib.SMTP(NotificationService.SMTP_SERVER, NotificationService.SMTP_PORT) as server:
                server.starttls()
                server.login(NotificationService.SMTP_USERNAME, NotificationService.SMTP_PASSWORD)
                server.sendmail(
                    NotificationService.SENDER_EMAIL,
                    recipient_email,
                    message.as_string()
                )
            
            logging.info(f"Email sent to {recipient_email}")
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
    
    @staticmethod
    def _load_template(template_name: str, template_data: Dict[str, Any]) -> str:
        """
        Load and populate an email template
        
        Args:
            template_name: Template file name
            template_data: Template data
            
        Returns:
            Populated template HTML
        """
        try:
            template_path = os.path.join(NotificationService.TEMPLATES_DIR, f"{template_name}.html")
            
            if not os.path.exists(template_path):
                # Return basic template if file doesn't exist
                return NotificationService._get_default_template(template_data)
            
            with open(template_path, "r") as f:
                template = f.read()
            
            # Replace variables in template
            for key, value in template_data.items():
                template = template.replace(f"{{{{{key}}}}}", str(value))
            
            return template
        except Exception as e:
            logging.error(f"Failed to load template: {e}")
            return NotificationService._get_default_template(template_data)
    
    @staticmethod
    def _get_default_template(template_data: Dict[str, Any]) -> str:
        """
        Get a default email template
        
        Args:
            template_data: Template data
            
        Returns:
            Default template HTML
        """
        title = template_data.get("title", "Notification")
        message = template_data.get("message", "You have a new notification from Trace.")
        button_text = template_data.get("button_text", "View Details")
        button_url = template_data.get("button_url", "https://trace.app")
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    line-height: 1.6; 
                    color: #333;
                    margin: 0;
                    padding: 0;
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 0 auto; 
                    padding: 20px;
                }}
                .header {{ 
                    background-color: #4a56e2; 
                    padding: 20px; 
                    text-align: center;
                    color: white;
                }}
                .content {{ 
                    padding: 20px; 
                    background-color: #f9f9f9;
                }}
                .button {{ 
                    display: inline-block; 
                    background-color: #4a56e2; 
                    color: white; 
                    padding: 10px 20px; 
                    text-decoration: none; 
                    border-radius: 4px;
                }}
                .footer {{ 
                    padding: 20px; 
                    text-align: center; 
                    font-size: 12px;
                    color: #666;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Trace</h1>
                </div>
                <div class="content">
                    <h2>{title}</h2>
                    <p>{message}</p>
                    <p style="text-align: center; margin-top: 30px;">
                        <a href="{button_url}" class="button">{button_text}</a>
                    </p>
                </div>
                <div class="footer">
                    <p>© {template_data.get("year", "2023")} Trace. All rights reserved.</p>
                    <p>This email was sent to you as a registered user of Trace.</p>
                </div>
            </div>
        </body>
        </html>
        """
    
    @staticmethod
    async def notify_low_credits(
        background_tasks: BackgroundTasks,
        db: Session,
        user_id: int,
        current_balance: int
    ):
        """
        Send a low credits notification
        
        Args:
            background_tasks: FastAPI BackgroundTasks
            db: Database session
            user_id: User ID
            current_balance: Current credit balance
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logging.error(f"User not found: {user_id}")
            return
        
        await NotificationService.send_email_notification(
            background_tasks,
            user.email,
            "Low Credit Balance",
            "low_credits",
            {
                "title": "Low Credit Balance",
                "message": f"Your credit balance is running low. You have {current_balance} credits remaining.",
                "button_text": "Buy Credits",
                "button_url": "https://trace.app/credits",
                "current_balance": current_balance,
                "year": "2023"
            }
        )
    
    @staticmethod
    async def notify_search_complete(
        background_tasks: BackgroundTasks,
        db: Session,
        user_id: int,
        job_id: str,
        query_type: str,
        results_url: str
    ):
        """
        Send a search completion notification
        
        Args:
            background_tasks: FastAPI BackgroundTasks
            db: Database session
            user_id: User ID
            job_id: Search job ID
            query_type: Query type
            results_url: Results URL
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logging.error(f"User not found: {user_id}")
            return
        
        query_type_display = {
            "light": "Text",
            "heavy": "Image/Audio",
            "video": "Video"
        }.get(query_type, query_type.capitalize())
        
        await NotificationService.send_email_notification(
            background_tasks,
            user.email,
            f"Your {query_type_display} Search Results are Ready",
            "search_complete",
            {
                "title": f"Your {query_type_display} Search Results are Ready",
                "message": f"Your Trace search job (ID: {job_id}) has completed processing. Click below to view the results.",
                "button_text": "View Results",
                "button_url": results_url,
                "job_id": job_id,
                "query_type": query_type_display,
                "year": "2023"
            }
        )
    
    @staticmethod
    async def notify_subscription_renewal(
        background_tasks: BackgroundTasks,
        db: Session,
        user_id: int,
        credits_added: int,
        new_balance: int,
        tier: str
    ):
        """
        Send a subscription renewal notification
        
        Args:
            background_tasks: FastAPI BackgroundTasks
            db: Database session
            user_id: User ID
            credits_added: Credits added
            new_balance: New credit balance
            tier: Subscription tier
        """
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            logging.error(f"User not found: {user_id}")
            return
        
        tier_display = tier.capitalize()
        
        await NotificationService.send_email_notification(
            background_tasks,
            user.email,
            f"Subscription Renewed - {credits_added} Credits Added",
            "subscription_renewal",
            {
                "title": f"{tier_display} Subscription Renewed",
                "message": f"Your {tier_display} subscription has been renewed. We've added {credits_added} credits to your account. Your new balance is {new_balance} credits.",
                "button_text": "View Account",
                "button_url": "https://trace.app/account",
                "credits_added": credits_added,
                "new_balance": new_balance,
                "tier": tier_display,
                "year": "2023"
            }
        ) 