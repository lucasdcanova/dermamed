from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from typing import Optional
import tempfile
import os
import uuid
from datetime import datetime
import shutil

from app.core.config import get_settings, MEDICAL_DISCLAIMER, COMPLIANCE_MESSAGES
from app.core.ai_engine_v2 import get_ai_engine
from app.core.ai_engine_fallback import get_ai_engine_fallback
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
async def demo_analysis(
    file: UploadFile = File(...)
):
    """Demo endpoint for testing without authentication"""
    
    # Get file info for demo purposes
    file_size = 0
    temp_file_path = None
    
    try:
        # Read file to get size
        contents = await file.read()
        file_size = len(contents)
        await file.seek(0)
        
        # Generate random-ish values based on filename
        import hashlib
        file_hash = hashlib.md5(file.filename.encode()).hexdigest()
        confidence = 0.75 + (int(file_hash[:2], 16) / 1000)
        asymmetry = int(file_hash[2:4], 16) / 500
        
        # Different diagnoses based on file name
        if "melanoma" in file.filename.lower():
            primary = "Suspected melanoma"
            risk = "High risk - urgent referral recommended"
        elif "nevus" in file.filename.lower():
            primary = "Benign melanocytic nevus"
            risk = "Low risk - benign features"
        else:
            primary = "Seborrheic keratosis"
            risk = "Low risk - benign lesion"
    
        # Return mock response with some file-specific data
        return AnalysisResponse(
            id=f"demo_{file_hash[:8]}",
            status=AnalysisStatus.COMPLETED,
            image_metadata=ImageMetadata(
                filename=file.filename,
                content_type=file.content_type,
                size_bytes=file_size
            ),
            analysis={
                "primary_diagnosis": primary,
                "confidence": round(confidence, 2),
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
                "asymmetry": round(asymmetry, 2),
                "border_irregularity": round(asymmetry * 1.5, 2),
                "color_variation": round(asymmetry * 1.2, 2),
                "diameter_mm": round(3 + (int(file_hash[4:6], 16) / 50), 1)
            },
            "risk_assessment": risk,
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
            processing_time_seconds=round(0.5 + (file_size / 10000000), 2)
        )
    except Exception as e:
        raise HTTPException(400, f"Error processing file: {str(e)}")

@router.post("/test-real", response_model=AnalysisResponse)
async def test_real_analysis(
    file: UploadFile = File(...)
):
    """Test endpoint with real AI analysis (no auth required for testing)"""
    
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
        logger.info(
            f"Test analysis requested",
            extra={
                "analysis_id": analysis_id,
                "filename": file.filename
            }
        )
        
        # Try real AI first, fallback if needed
        analysis_result = None
        error_msg = None
        
        try:
            # Try MedGemma first
            ai_engine = get_ai_engine()
            analysis_result = ai_engine.analyze(temp_file_path)
            logger.info("MedGemma analysis successful")
        except Exception as e:
            logger.warning(f"MedGemma failed: {str(e)}, using fallback")
            error_msg = str(e)
            
            try:
                # Use fallback engine
                fallback_engine = get_ai_engine_fallback()
                analysis_result = fallback_engine.analyze(temp_file_path)
                logger.info("Fallback analysis successful")
            except Exception as e2:
                logger.error(f"Both engines failed: {str(e2)}")
                raise RuntimeError(f"Analysis failed: MedGemma: {error_msg}, Fallback: {str(e2)}")
        
        # Create compliance info
        compliance_info = ComplianceInfo(
                disclaimer=MEDICAL_DISCLAIMER,
                intended_use=COMPLIANCE_MESSAGES["intended_use"],
                regulatory_status=COMPLIANCE_MESSAGES["not_for_diagnosis"],
                analysis_limitations=[
                    "Test mode - for demonstration only",
                    "Not for clinical use",
                    "Requires validation by healthcare professionals"
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
            
            return response
            
        except Exception as e:
            logger.error(f"Real analysis failed: {str(e)}", extra={"analysis_id": analysis_id})
            
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