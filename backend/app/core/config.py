from pydantic_settings import BaseSettings
from typing import List
import os
from functools import lru_cache

class Settings(BaseSettings):
    app_name: str = "DermaMed"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API Settings
    api_v1_str: str = "/api/v1"
    secret_key: str
    
    # Database
    database_url: str
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # AI Model
    model_name: str = "google/medgemma-4b-it"
    huggingface_token: str = ""
    inference_timeout: int = 60  # seconds
    
    # Security
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]
    
    # File Upload
    max_upload_size: int = 52428800  # 50MB
    allowed_extensions: List[str] = ["jpg", "jpeg", "png", "bmp", "tiff"]
    
    # Compliance
    enable_compliance_mode: bool = True
    audit_log_enabled: bool = True
    
    # Storage
    upload_dir: str = "./uploads"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

@lru_cache()
def get_settings():
    return Settings()

# Medical disclaimer constant
MEDICAL_DISCLAIMER = """
This AI-powered analysis is intended for use by qualified healthcare professionals 
as a clinical decision support tool only. It should not be used as the sole basis 
for diagnosis or treatment decisions. Always consult with appropriate medical 
professionals and consider the full clinical context when making medical decisions.

This software has not been evaluated by the FDA or other regulatory bodies for 
diagnostic use. It is not intended to diagnose, treat, cure, or prevent any disease.
"""

# Compliance messages
COMPLIANCE_MESSAGES = {
    "intended_use": "For professional medical use only - Clinical decision support",
    "not_for_diagnosis": "Not approved for standalone diagnostic use",
    "seek_medical_advice": "Always consult qualified healthcare professionals",
    "data_privacy": "All data is processed in compliance with HIPAA and GDPR requirements",
    "version_info": "DermaMed v1.0.0 - Research Use Only"
}