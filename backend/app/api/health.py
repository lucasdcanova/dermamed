from fastapi import APIRouter, Depends
from datetime import datetime
import psutil
import torch

from app.core.config import get_settings

router = APIRouter()
settings = get_settings()

@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": settings.app_version
    }

@router.get("/system")
async def system_health():
    """Detailed system health information"""
    
    # Check GPU availability
    gpu_available = torch.cuda.is_available()
    gpu_count = torch.cuda.device_count() if gpu_available else 0
    
    # System metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "system": {
            "cpu_usage_percent": cpu_percent,
            "memory_usage_percent": memory.percent,
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "gpu_available": gpu_available,
            "gpu_count": gpu_count
        },
        "ml_backend": {
            "torch_version": torch.__version__,
            "cuda_available": gpu_available,
            "model_loaded": False  # Will be updated when model is loaded
        }
    }