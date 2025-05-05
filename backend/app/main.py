from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, credits, search, audio, video
from .models.db import engine, Base
from .services.scheduler_service import SchedulerService

# Create tables
Base.metadata.create_all(bind=engine)

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

# Include routers
app.include_router(auth.router)
app.include_router(credits.router)
app.include_router(search.router)
app.include_router(audio.router)
app.include_router(video.router)

@app.on_event("startup")
async def startup_event():
    # Start the scheduler when the application starts
    await SchedulerService.start()

@app.on_event("shutdown")
async def shutdown_event():
    # Stop the scheduler when the application shuts down
    await SchedulerService.stop()

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