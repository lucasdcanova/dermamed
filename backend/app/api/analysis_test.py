from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
import tempfile
import os
import uuid
from datetime import datetime
import logging

from app.core.config import get_settings, MEDICAL_DISCLAIMER, COMPLIANCE_MESSAGES
from app.core.ai_engine_fallback import get_ai_engine_fallback
from app.schemas.analysis import (
    AnalysisResponse, 
    AnalysisStatus,
    ImageMetadata,
    ComplianceInfo
)

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)

@router.post("/test-ai", response_model=AnalysisResponse)
async def test_ai_analysis(
    file: UploadFile = File(...)
):
    """Test endpoint with AI analysis (using fallback for now)"""
    
    # Generate analysis ID
    analysis_id = f"test_{uuid.uuid4().hex[:12]}"
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(400, "File must be an image")
    
    # Check file size
    file_size = 0
    temp_file_path = None
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            contents = await file.read()
            tmp.write(contents)
            temp_file_path = tmp.name
            file_size = len(contents)
        
        # Validate file size
        if file_size > settings.max_upload_size:
            raise HTTPException(413, f"File too large. Maximum size: {settings.max_upload_size / 1024 / 1024:.1f}MB")
        
        # Create image metadata
        image_metadata = ImageMetadata(
            filename=file.filename,
            content_type=file.content_type,
            size_bytes=file_size
        )
        
        # Log analysis request
        logger.info(f"Test AI analysis requested for {file.filename}")
        
        # Get fallback AI engine (more reliable than MedGemma API)
        ai_engine = get_ai_engine_fallback()
        
        # Perform analysis
        analysis_result = ai_engine.analyze(temp_file_path)
        
        # Create compliance info
        compliance_info = ComplianceInfo(
            disclaimer=MEDICAL_DISCLAIMER,
            intended_use=COMPLIANCE_MESSAGES["intended_use"],
            regulatory_status=COMPLIANCE_MESSAGES["not_for_diagnosis"],
            analysis_limitations=[
                "Test mode - using simplified AI analysis",
                "Not for clinical use",
                "For demonstration purposes only"
            ]
        )
        
        # Create response
        response = AnalysisResponse(
            id=analysis_id,
            status=AnalysisStatus.COMPLETED,
            image_metadata=image_metadata,
            analysis=analysis_result,
            compliance=compliance_info,
            processing_time_seconds=getattr(analysis_result, 'processing_time', 1.0)
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Test AI analysis failed: {str(e)}")
        
        # Return error response
        return AnalysisResponse(
            id=analysis_id,
            status=AnalysisStatus.FAILED,
            image_metadata=ImageMetadata(
                filename=file.filename,
                content_type=file.content_type,
                size_bytes=file_size
            ),
            compliance=ComplianceInfo(
                disclaimer=MEDICAL_DISCLAIMER,
                intended_use=COMPLIANCE_MESSAGES["intended_use"],
                regulatory_status=COMPLIANCE_MESSAGES["not_for_diagnosis"],
                analysis_limitations=["Analysis could not be completed"]
            ),
            error_message=f"Analysis failed: {str(e)}"
        )
        
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)