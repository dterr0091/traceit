import os
import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from .routers import auth, credits, search, audio, video, spread
from .models.db import engine, Base
from .services.scheduler_service import SchedulerService
from .services.lineage_service import LineageService

# Create tables
Base.metadata.create_all(bind=engine)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Initialize FastAPI app
app = FastAPI(
    title="Trace API",
    description="API for Trace - Content Origin Verification Service",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv("SESSION_SECRET_KEY", "dev_session_key"),
    max_age=60 * 60 * 24 * 7,  # 1 week
)

# Include routers
app.include_router(auth.router)
app.include_router(credits.router)
app.include_router(search.router)
app.include_router(audio.router)
app.include_router(video.router)
app.include_router(spread.router)

# Initialize services
scheduler_service = SchedulerService()
lineage_service = LineageService()

@app.on_event("startup")
async def startup_event():
    """Initialize services and connections on app startup."""
    # Log app startup
    logging.info("Starting Trace API")
    
    # Initialize Neo4j connection if needed
    if lineage_service.neo4j_enabled:
        logging.info("Neo4j lineage graph is enabled")
    else:
        logging.info("Neo4j lineage graph is disabled - using Redis for lineage storage")

    # Start the scheduler when the application starts
    await scheduler_service.start()

@app.on_event("shutdown")
async def shutdown_event():
    """Clean up resources on application shutdown."""
    # Stop the scheduler
    await scheduler_service.stop()
    
    # Close Neo4j connection if it exists
    await lineage_service.close()

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Trace API",
        "docs": "/docs",
        "version": "0.1.0"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"} 