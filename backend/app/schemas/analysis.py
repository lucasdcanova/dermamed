from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum

class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class LesionCharacteristics(BaseModel):
    asymmetry: Optional[float] = Field(None, ge=0, le=1)
    border_irregularity: Optional[float] = Field(None, ge=0, le=1)
    color_variation: Optional[float] = Field(None, ge=0, le=1)
    diameter_mm: Optional[float] = Field(None, gt=0)
    evolution: Optional[str] = None

class DifferentialDiagnosis(BaseModel):
    condition: str
    probability: float = Field(ge=0, le=1)
    icd10_code: Optional[str] = None
    description: Optional[str] = None

class ImageMetadata(BaseModel):
    filename: str
    content_type: str
    size_bytes: int
    dimensions: Optional[Dict[str, int]] = None
    upload_timestamp: datetime = Field(default_factory=datetime.utcnow)

class AnalysisRequest(BaseModel):
    clinical_history: Optional[str] = Field(None, max_length=2000)
    patient_age: Optional[int] = Field(None, ge=0, le=150)
    patient_sex: Optional[str] = Field(None, pattern="^(M|F|O)$")
    lesion_location: Optional[str] = None
    symptoms_duration: Optional[str] = None
    previous_treatments: Optional[List[str]] = []
    
    class Config:
        json_schema_extra = {
            "example": {
                "clinical_history": "Patient noticed changing mole over 3 months",
                "patient_age": 45,
                "patient_sex": "F",
                "lesion_location": "Upper back",
                "symptoms_duration": "3 months"
            }
        }

class AnalysisResult(BaseModel):
    primary_diagnosis: str
    confidence: float = Field(ge=0, le=1)
    differential_diagnoses: List[DifferentialDiagnosis]
    lesion_characteristics: Optional[LesionCharacteristics] = None
    risk_assessment: str
    recommendations: List[str]
    requires_biopsy: bool
    follow_up_interval: Optional[str] = None
    
class ComplianceInfo(BaseModel):
    disclaimer: str
    intended_use: str
    regulatory_status: str
    analysis_limitations: List[str]
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AnalysisResponse(BaseModel):
    id: str
    status: AnalysisStatus
    image_metadata: ImageMetadata
    analysis: Optional[AnalysisResult] = None
    compliance: ComplianceInfo
    processing_time_seconds: Optional[float] = None
    error_message: Optional[str] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "analysis_123456",
                "status": "completed",
                "image_metadata": {
                    "filename": "lesion.jpg",
                    "content_type": "image/jpeg",
                    "size_bytes": 1024000
                },
                "analysis": {
                    "primary_diagnosis": "Benign nevus",
                    "confidence": 0.92,
                    "differential_diagnoses": [
                        {
                            "condition": "Melanoma",
                            "probability": 0.05,
                            "icd10_code": "C43.9"
                        }
                    ],
                    "risk_assessment": "Low risk",
                    "recommendations": [
                        "Routine monitoring recommended",
                        "Follow-up in 6 months"
                    ],
                    "requires_biopsy": False
                },
                "compliance": {
                    "disclaimer": "For clinical decision support only",
                    "intended_use": "Professional medical use",
                    "regulatory_status": "Not FDA approved",
                    "analysis_limitations": [
                        "Not for standalone diagnosis",
                        "Requires clinical correlation"
                    ]
                }
            }
        }