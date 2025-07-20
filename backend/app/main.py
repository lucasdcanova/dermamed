from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import os

from app.core.config import get_settings
from app.api import health, analysis, auth
from app.core.logging_config import setup_logging

settings = get_settings()
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    
    # Create necessary directories
    os.makedirs(settings.upload_dir, exist_ok=True)
    os.makedirs("./models", exist_ok=True)  # Keep models dir for future use
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="AI-powered dermatological analysis system for healthcare professionals",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(auth.router, prefix=f"{settings.api_v1_str}/auth", tags=["authentication"])
app.include_router(analysis.router, prefix=f"{settings.api_v1_str}/analysis", tags=["analysis"])

@app.get("/")
async def root():
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "operational",
        "compliance": {
            "disclaimer": "For professional medical use only",
            "regulatory_status": "Not FDA approved for diagnostic use"
        }
    }