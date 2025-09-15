from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import gc
from contextlib import asynccontextmanager
from .settings import get_settings
from .routes import router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for the FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting up Document Content Extractor service...")
    gc.collect()  # Initial garbage collection
    
    try:
        yield
    finally:
        # Shutdown
        logger.info("Shutting down Document Content Extractor service...")
        # Perform cleanup
        gc.collect()
        logger.info("Cleanup completed")

def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    settings = get_settings()
    
    app = FastAPI(
        title="Document Content Extractor",
        description="Microservice for extracting content from documents using unstructured",
        lifespan=lifespan  # Add lifecycle management
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routes
    app.include_router(router)
    
    return app

app = create_application()

# Add startup and shutdown event handlers for additional cleanup
@app.on_event("startup")
async def startup_event():
    """Additional startup tasks"""
    logger.info("Performing additional startup tasks...")
    # Clear any temporary files that might have been left from previous runs
    # You might want to add cleanup of specific directories here
    
@app.on_event("shutdown")
async def shutdown_event():
    """Additional shutdown tasks"""
    logger.info("Performing additional shutdown tasks...")
    # Additional cleanup tasks
    gc.collect()  # Final garbage collection