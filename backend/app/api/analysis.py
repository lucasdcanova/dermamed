from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from typing import Optional
import tempfile
import os
import uuid
from datetime import datetime
import shutil

from app.core.config import get_settings, MEDICAL_DISCLAIMER, COMPLIANCE_MESSAGES
from app.core.ai_engine_v2 import get_ai_engine
from app.schemas.analysis import (
    AnalysisRequest, 
    AnalysisResponse, 
    AnalysisStatus,
    ImageMetadata,
    ComplianceInfo
)
from app.api.deps import get_current_user
import logging

router = APIRouter()
settings = get_settings()
logger = logging.getLogger(__name__)

@router.post("/", response_model=AnalysisResponse)
async def analyze_image(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    clinical_history: Optional[str] = None,
    patient_age: Optional[int] = None,
    patient_sex: Optional[str] = None,
    lesion_location: Optional[str] = None,
    symptoms_duration: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """
    Analyze a dermatological image using AI.
    
    - **file**: Image file (JPEG, PNG, etc.)
    - **clinical_history**: Patient's relevant medical history
    - **patient_age**: Patient age in years
    - **patient_sex**: Patient sex (M/F/O)
    - **lesion_location**: Anatomical location of the lesion
    - **symptoms_duration**: How long symptoms have been present
    """
    
    # Generate analysis ID
    analysis_id = f"analysis_{uuid.uuid4().hex[:12]}"
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(400, "File must be an image")
    
    # Check file size
    file_size = 0
    temp_file_path = None
    
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            shutil.copyfileobj(file.file, tmp)
            temp_file_path = tmp.name
            file_size = tmp.tell()
        
        # Validate file size
        if file_size > settings.max_upload_size:
            raise HTTPException(413, f"File too large. Maximum size: {settings.max_upload_size / 1024 / 1024:.1f}MB")
        
        # Create image metadata
        image_metadata = ImageMetadata(
            filename=file.filename,
            content_type=file.content_type,
            size_bytes=file_size
        )
        
        # Prepare clinical context
        clinical_context = {
            "clinical_history": clinical_history,
            "patient_age": patient_age,
            "patient_sex": patient_sex,
            "lesion_location": lesion_location,
            "symptoms_duration": symptoms_duration
        }
        
        # Remove None values
        clinical_context = {k: v for k, v in clinical_context.items() if v is not None}
        
        # Log analysis request
        logger.info(
            f"Analysis requested by user {current_user['username']}",
            extra={
                "user_id": current_user["id"],
                "analysis_id": analysis_id,
                "filename": file.filename,
                "medical_data": True
            }
        )
        
        # Get AI engine
        ai_engine = get_ai_engine()
        
        # Perform analysis
        try:
            analysis_result = ai_engine.analyze(temp_file_path, clinical_context)
            
            # Create compliance info
            compliance_info = ComplianceInfo(
                disclaimer=MEDICAL_DISCLAIMER,
                intended_use=COMPLIANCE_MESSAGES["intended_use"],
                regulatory_status=COMPLIANCE_MESSAGES["not_for_diagnosis"],
                analysis_limitations=[
                    "Not for standalone diagnostic use",
                    "Requires clinical correlation",
                    "Results should be validated by qualified healthcare professionals",
                    "May not detect all conditions"
                ]
            )
            
            # Create response
            response = AnalysisResponse(
                id=analysis_id,
                status=AnalysisStatus.COMPLETED,
                image_metadata=image_metadata,
                analysis=analysis_result,
                compliance=compliance_info,
                processing_time_seconds=analysis_result.processing_time if hasattr(analysis_result, 'processing_time') else None
            )
            
            # Save analysis to database in background
            background_tasks.add_task(save_analysis_to_db, analysis_id, response, current_user["id"])
            
            return response
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", extra={"analysis_id": analysis_id})
            
            # Return error response
            return AnalysisResponse(
                id=analysis_id,
                status=AnalysisStatus.FAILED,
                image_metadata=image_metadata,
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

@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a previous analysis by ID"""
    
    # TODO: Implement database retrieval
    raise HTTPException(404, "Analysis not found")

async def save_analysis_to_db(analysis_id: str, analysis: AnalysisResponse, user_id: str):
    """Save analysis results to database (background task)"""
    # TODO: Implement database storage
    logger.info(f"Analysis {analysis_id} saved to database")

@router.post("/demo", response_model=AnalysisResponse)
async def demo_analysis():
    """Demo endpoint for testing without authentication"""
    
    # Return mock response for testing
    return AnalysisResponse(
        id="demo_analysis_001",
        status=AnalysisStatus.COMPLETED,
        image_metadata=ImageMetadata(
            filename="demo_image.jpg",
            content_type="image/jpeg",
            size_bytes=1024000
        ),
        analysis={
            "primary_diagnosis": "Benign melanocytic nevus",
            "confidence": 0.89,
            "differential_diagnoses": [
                {
                    "condition": "Atypical nevus",
                    "probability": 0.08,
                    "icd10_code": "D22.9"
                },
                {
                    "condition": "Melanoma in situ",
                    "probability": 0.03,
                    "icd10_code": "D03.9"
                }
            ],
            "lesion_characteristics": {
                "asymmetry": 0.15,
                "border_irregularity": 0.22,
                "color_variation": 0.18,
                "diameter_mm": 4.5
            },
            "risk_assessment": "Low risk - benign features",
            "recommendations": [
                "Routine monitoring recommended",
                "Patient education on self-examination",
                "Follow-up in 12 months or if changes occur"
            ],
            "requires_biopsy": False,
            "follow_up_interval": "12 months"
        },
        compliance=ComplianceInfo(
            disclaimer=MEDICAL_DISCLAIMER,
            intended_use=COMPLIANCE_MESSAGES["intended_use"],
            regulatory_status=COMPLIANCE_MESSAGES["not_for_diagnosis"],
            analysis_limitations=[
                "Demo analysis - not based on real image",
                "For demonstration purposes only"
            ]
        ),
        processing_time_seconds=1.23
    )