from fastapi import APIRouter

from app.api.v1 import auth, users, search, credits, origins, bundles

api_router = APIRouter()

# Include API v1 routers
api_router.include_router(auth.router, prefix="/v1/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/v1/users", tags=["users"])
api_router.include_router(search.router, prefix="/v1/search", tags=["search"])
api_router.include_router(credits.router, prefix="/v1/credits", tags=["credits"])
api_router.include_router(origins.router, prefix="/v1/origins", tags=["origins"])
api_router.include_router(bundles.router, prefix="/v1/bundles", tags=["bundles"]) 