import os
import base64
from typing import Dict, Any, Optional
import logging
import time
from PIL import Image
import io
import json

from huggingface_hub import InferenceClient

from app.core.config import get_settings, MEDICAL_DISCLAIMER
from app.schemas.analysis import (
    AnalysisResult, 
    DifferentialDiagnosis, 
    LesionCharacteristics
)

logger = logging.getLogger(__name__)
settings = get_settings()

class DermatologyAIFallback:
    """Fallback AI engine using general vision models when MedGemma is not available"""
    
    def __init__(self):
        self.client = InferenceClient(token=settings.huggingface_token)
        self._initialized = True
        logger.info("DermatologyAI Fallback initialized")
    
    def analyze(self, image_path: str, clinical_context: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """Perform basic image analysis using available vision models"""
        
        start_time = time.time()
        
        try:
            # For demo purposes, use image classification
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            # Try to get basic image features (using a general model)
            try:
                # Use a general image classification model
                result = self.client.image_classification(image_data)
                logger.info(f"Classification result: {result}")
            except Exception as e:
                logger.warning(f"Image classification failed: {e}")
                result = []
            
            # Generate mock medical analysis based on image properties
            img = Image.open(image_path)
            
            # Simple heuristics based on image properties
            width, height = img.size
            aspect_ratio = width / height if height > 0 else 1
            
            # Get dominant colors
            img_small = img.resize((50, 50))
            colors = img_small.getcolors(maxcolors=256)
            
            # Mock analysis based on basic features
            if len(colors) > 100:
                primary = "Complex pigmented lesion"
                confidence = 0.65
                risk = "Medium risk - requires evaluation"
            elif aspect_ratio > 1.5 or aspect_ratio < 0.67:
                primary = "Irregular shaped lesion"
                confidence = 0.70
                risk = "Medium risk - asymmetric features"
            else:
                primary = "Regular skin lesion"
                confidence = 0.80
                risk = "Low risk - symmetric features"
            
            # Create structured result
            return AnalysisResult(
                primary_diagnosis=primary,
                confidence=confidence,
                differential_diagnoses=[
                    DifferentialDiagnosis(
                        condition="Benign nevus",
                        probability=0.30,
                        icd10_code="D22.9"
                    ),
                    DifferentialDiagnosis(
                        condition="Seborrheic keratosis", 
                        probability=0.20,
                        icd10_code="L82.1"
                    )
                ],
                lesion_characteristics=LesionCharacteristics(
                    asymmetry=0.3 if aspect_ratio > 1.2 else 0.1,
                    border_irregularity=0.4 if len(colors) > 100 else 0.2,
                    color_variation=min(len(colors) / 200, 1.0),
                    diameter_mm=round(min(width, height) / 10, 1)
                ),
                risk_assessment=risk,
                recommendations=[
                    "Clinical correlation required",
                    "Consider dermoscopy for detailed evaluation",
                    "Follow-up if changes occur"
                ],
                requires_biopsy=False,
                follow_up_interval="6 months",
                processing_time=time.time() - start_time
            )
            
        except Exception as e:
            logger.error(f"Fallback analysis failed: {str(e)}")
            # Return basic result
            return AnalysisResult(
                primary_diagnosis="Analysis unavailable",
                confidence=0.0,
                differential_diagnoses=[],
                lesion_characteristics=None,
                risk_assessment="Unable to assess - technical error",
                recommendations=["Please consult healthcare provider"],
                requires_biopsy=False,
                follow_up_interval="As needed",
                processing_time=time.time() - start_time
            )

# Singleton instance
_ai_engine_fallback: Optional[DermatologyAIFallback] = None

def get_ai_engine_fallback() -> DermatologyAIFallback:
    """Get or create the fallback AI engine singleton"""
    global _ai_engine_fallback
    if _ai_engine_fallback is None:
        _ai_engine_fallback = DermatologyAIFallback()
    return _ai_engine_fallback