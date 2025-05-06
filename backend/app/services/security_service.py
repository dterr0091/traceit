import logging
import os
import time
import json
from typing import Dict, Any, List, Optional, Callable
from fastapi import Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import redis.asyncio as redis
import uuid
import hashlib
from datetime import datetime, timedelta

class RateLimiter(BaseHTTPMiddleware):
    """
    Rate limiting middleware to prevent abuse of the API
    
    Limits requests based on IP address and optional user ID
    """
    def __init__(self, app: ASGIApp, redis_url: Optional[str] = None):
        super().__init__(app)
        self.redis_url = redis_url or os.getenv("REDIS_URL")
        self.redis_client = None
        self.rate_limits = {
            # path: (requests, period in seconds)
            "/api/search": (60, 60),  # 60 requests per minute for general search
            "/api/video/process": (10, 60),  # 10 video requests per minute
            "/api/image/process": (30, 60),  # 30 image requests per minute
            "/api/audio/process": (30, 60),  # 30 audio requests per minute
            "/api/auth": (20, 60),  # 20 auth requests per minute
        }
        self.default_limit = (120, 60)  # Default: 120 requests per minute
        
        # Initialize Redis connection
        self._init_redis()
    
    async def _init_redis(self):
        """Initialize Redis connection"""
        if self.redis_url:
            try:
                self.redis_client = await redis.from_url(self.redis_url)
                logging.info("Rate limiter Redis connection established")
            except Exception as e:
                logging.error(f"Failed to connect to Redis for rate limiting: {e}")
                self.redis_client = None
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Rate limit requests based on IP address and path
        
        Args:
            request: FastAPI request
            call_next: Next middleware in the chain
            
        Returns:
            Response
        """
        # Skip rate limiting if Redis is not available
        if not self.redis_client:
            return await call_next(request)
        
        # Get client IP address
        client_ip = request.client.host if request.client else "unknown"
        
        # Get user ID from token if available
        user_id = await self._get_user_id_from_request(request)
        
        # Determine rate limit for this path
        path = request.url.path
        for limit_path, limits in self.rate_limits.items():
            if path.startswith(limit_path):
                max_requests, period = limits
                break
        else:
            max_requests, period = self.default_limit
        
        # Create rate limit key
        rate_limit_key = f"ratelimit:{client_ip}:{path}"
        if user_id:
            rate_limit_key = f"ratelimit:{user_id}:{path}"
        
        # Check if rate limit exceeded
        current_count = await self.redis_client.get(rate_limit_key)
        if current_count is not None and int(current_count) >= max_requests:
            # Rate limit exceeded
            logging.warning(f"Rate limit exceeded for {rate_limit_key}")
            
            # Get time to reset
            ttl = await self.redis_client.ttl(rate_limit_key)
            
            return Response(
                content=json.dumps({
                    "detail": "Rate limit exceeded. Please try again later.",
                    "reset_in_seconds": ttl if ttl > 0 else period
                }),
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json"
            )
        
        # Increment rate limit counter
        if not await self.redis_client.exists(rate_limit_key):
            await self.redis_client.set(rate_limit_key, 1, ex=period)
        else:
            await self.redis_client.incr(rate_limit_key)
        
        # Continue processing request
        return await call_next(request)
    
    async def _get_user_id_from_request(self, request: Request) -> Optional[str]:
        """Extract user ID from request authorization"""
        try:
            if "authorization" in request.headers:
                auth_header = request.headers["authorization"]
                if auth_header.startswith("Bearer "):
                    token = auth_header.replace("Bearer ", "")
                    # In a real app, you'd verify and decode the token here
                    # This is just a simple example
                    return hashlib.md5(token.encode()).hexdigest()
        except Exception:
            pass
        return None

class SecurityHeaders(BaseHTTPMiddleware):
    """
    Middleware to add security headers to responses
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src 'self'"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

class RequestLogger(BaseHTTPMiddleware):
    """
    Middleware to log request details
    """
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        # Add request ID to request state for logging
        request.state.request_id = request_id
        
        # Log request
        logging.info(
            f"Request {request_id} started: {request.method} {request.url.path} "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        try:
            response = await call_next(request)
            
            # Log response
            process_time = round((time.time() - start_time) * 1000, 2)
            logging.info(
                f"Request {request_id} completed: {response.status_code} "
                f"Process time: {process_time}ms"
            )
            
            # Add request ID and processing time to response headers
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
        except Exception as e:
            logging.error(f"Request {request_id} failed: {e}")
            raise
    
class SecurityService:
    """
    Security configuration and utility methods for production hardening
    """
    @staticmethod
    def setup_cors(app, allowed_origins: Optional[List[str]] = None):
        """
        Configure CORS middleware
        
        Args:
            app: FastAPI app
            allowed_origins: List of allowed origins
            
        Returns:
            None
        """
        if not allowed_origins:
            allowed_origins = [
                "http://localhost:3000",
                "https://trace.app"
            ]
            
            # Add environment-specific origins
            env_origin = os.getenv("ALLOWED_ORIGIN")
            if env_origin:
                allowed_origins.append(env_origin)
        
        app.add_middleware(
            CORSMiddleware,
            allow_origins=allowed_origins,
            allow_credentials=True,
            allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            allow_headers=["*"],
        )
    
    @staticmethod
    def setup_security_middlewares(app, redis_url: Optional[str] = None):
        """
        Configure security middlewares
        
        Args:
            app: FastAPI app
            redis_url: Redis URL for rate limiting
            
        Returns:
            None
        """
        # Add security headers
        app.add_middleware(SecurityHeaders)
        
        # Add request logging
        app.add_middleware(RequestLogger)
        
        # Add rate limiting if Redis URL provided
        if redis_url or os.getenv("REDIS_URL"):
            app.add_middleware(RateLimiter, redis_url=redis_url)
            
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Create a secure hash of a password
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password
        """
        salt = os.urandom(32)
        key = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            100000
        )
        return salt.hex() + ':' + key.hex()
    
    @staticmethod
    def verify_password(stored_password: str, provided_password: str) -> bool:
        """
        Verify a password against a stored hash
        
        Args:
            stored_password: Stored password hash
            provided_password: Plain text password to verify
            
        Returns:
            True if password is correct, False otherwise
        """
        salt_hex, key_hex = stored_password.split(':')
        salt = bytes.fromhex(salt_hex)
        key = bytes.fromhex(key_hex)
        
        new_key = hashlib.pbkdf2_hmac(
            'sha256',
            provided_password.encode('utf-8'),
            salt,
            100000
        )
        
        return key == new_key
    
    @staticmethod
    def generate_secure_token() -> str:
        """
        Generate a secure random token
        
        Returns:
            Secure token string
        """
        return uuid.uuid4().hex + uuid.uuid4().hex 