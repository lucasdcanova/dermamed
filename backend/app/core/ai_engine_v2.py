import os
import base64
from typing import Dict, Any, Optional
import logging
import time
from PIL import Image
import io

from huggingface_hub import InferenceClient

from app.core.config import get_settings, MEDICAL_DISCLAIMER
from app.schemas.analysis import (
    AnalysisResult, 
    DifferentialDiagnosis, 
    LesionCharacteristics
)

logger = logging.getLogger(__name__)
settings = get_settings()

class DermatologyAI:
    """AI engine for dermatological image analysis using MedGemma via Inference API"""
    
    def __init__(self):
        self.client = InferenceClient(
            token=settings.huggingface_token
        )
        self._initialized = True
        logger.info("DermatologyAI initialized with Hugging Face Inference API")
    
    def image_to_base64(self, image_path: str) -> str:
        """Convert image to base64 string"""
        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Resize if too large (max 1024x1024 for API)
                max_size = 1024
                if img.width > max_size or img.height > max_size:
                    img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
                
                # Convert to base64
                buffer = io.BytesIO()
                img.save(buffer, format='JPEG', quality=95)
                img_str = base64.b64encode(buffer.getvalue()).decode()
                
                return f"data:image/jpeg;base64,{img_str}"
                
        except Exception as e:
            logger.error(f"Failed to convert image: {str(e)}")
            raise ValueError(f"Failed to process image: {str(e)}")
    
    def analyze(self, image_path: str, clinical_context: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """Perform dermatological analysis on an image using MedGemma"""
        
        start_time = time.time()
        
        try:
            # Convert image to base64
            image_base64 = self.image_to_base64(image_path)
            
            # Build analysis prompt
            prompt = self._build_analysis_prompt(clinical_context)
            
            # Prepare messages for the model
            messages = [
                {
                    "role": "system",
                    "content": "You are MedGemma, a medical AI assistant specialized in dermatology. Provide detailed clinical analysis of skin lesions."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_base64
                            }
                        }
                    ]
                }
            ]
            
            # Call MedGemma via Inference API
            completion = self.client.chat.completions.create(
                model="google/medgemma-4b-it",
                messages=messages,
                max_tokens=1024,
                temperature=0.7
            )
            
            # Extract response
            response = completion.choices[0].message.content
            
            # Parse the model's response into structured format
            analysis_result = self._parse_model_response(response)
            
            # Add processing time
            analysis_result.processing_time = time.time() - start_time
            
            # Log for audit
            logger.info(
                "Analysis completed",
                extra={
                    "medical_data": True,
                    "processing_time": analysis_result.processing_time,
                    "primary_diagnosis": analysis_result.primary_diagnosis
                }
            )
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            raise RuntimeError(f"Analysis failed: {str(e)}")
    
    def _build_analysis_prompt(self, clinical_context: Optional[Dict[str, Any]] = None) -> str:
        """Build the prompt for MedGemma analysis"""
        
        prompt_parts = [
            "Analyze this dermatological image and provide a comprehensive clinical assessment.",
            "",
            "Please include:",
            "1. PRIMARY DIAGNOSIS: Most likely diagnosis with confidence percentage",
            "2. DIFFERENTIAL DIAGNOSES: List 2-3 alternative diagnoses with probabilities",
            "3. LESION CHARACTERISTICS: Assess ABCDE criteria if applicable:",
            "   - Asymmetry (0-1 score)",
            "   - Border irregularity (0-1 score)",
            "   - Color variation (0-1 score)",
            "   - Diameter (estimate in mm)",
            "   - Evolution (if mentioned in history)",
            "4. RISK ASSESSMENT: Low/Medium/High risk with explanation",
            "5. RECOMMENDATIONS: Specific next steps",
            "6. BIOPSY: Yes/No with justification",
            "7. FOLLOW-UP: Suggested interval"
        ]
        
        if clinical_context:
            prompt_parts.append("\nCLINICAL CONTEXT:")
            if clinical_context.get("clinical_history"):
                prompt_parts.append(f"- History: {clinical_context['clinical_history']}")
            if clinical_context.get("patient_age"):
                prompt_parts.append(f"- Age: {clinical_context['patient_age']} years")
            if clinical_context.get("patient_sex"):
                sex_map = {"M": "Male", "F": "Female", "O": "Other"}
                prompt_parts.append(f"- Sex: {sex_map.get(clinical_context['patient_sex'], 'Unknown')}")
            if clinical_context.get("lesion_location"):
                prompt_parts.append(f"- Location: {clinical_context['lesion_location']}")
            if clinical_context.get("symptoms_duration"):
                prompt_parts.append(f"- Duration: {clinical_context['symptoms_duration']}")
        
        prompt_parts.append(
            "\nIMPORTANT: Provide structured analysis in the format requested above. "
            "Be specific and clinically accurate."
        )
        
        return "\n".join(prompt_parts)
    
    def _parse_model_response(self, response: str) -> AnalysisResult:
        """Parse MedGemma's response into structured format"""
        
        # Initialize default values
        primary_diagnosis = "Analysis pending"
        confidence = 0.0
        differential_diagnoses = []
        lesion_characteristics = None
        risk_assessment = "Requires clinical correlation"
        recommendations = ["Professional medical evaluation recommended"]
        requires_biopsy = False
        follow_up_interval = "As clinically indicated"
        
        # Parse response sections
        lines = response.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Identify sections
            if "PRIMARY DIAGNOSIS:" in line.upper():
                current_section = "primary"
                diagnosis_text = line.split(':', 1)[1].strip() if ':' in line else ""
                # Extract diagnosis and confidence
                if "%" in diagnosis_text or "confidence" in diagnosis_text.lower():
                    import re
                    # Try to extract percentage
                    match = re.search(r'(\d+(?:\.\d+)?)\s*%', diagnosis_text)
                    if match:
                        confidence = float(match.group(1)) / 100
                    # Extract diagnosis name
                    primary_diagnosis = re.sub(r'\s*\(?[\d.]+\s*%.*?\)?', '', diagnosis_text).strip()
                else:
                    primary_diagnosis = diagnosis_text
                    
            elif "DIFFERENTIAL DIAGNOSES:" in line.upper():
                current_section = "differential"
                
            elif "LESION CHARACTERISTICS:" in line.upper() or "ABCDE" in line.upper():
                current_section = "characteristics"
                
            elif "RISK ASSESSMENT:" in line.upper():
                current_section = "risk"
                risk_text = line.split(':', 1)[1].strip() if ':' in line else ""
                if risk_text:
                    risk_assessment = risk_text
                    
            elif "RECOMMENDATIONS:" in line.upper():
                current_section = "recommendations"
                recommendations = []
                
            elif "BIOPSY:" in line.upper():
                current_section = "biopsy"
                if "yes" in line.lower():
                    requires_biopsy = True
                    
            elif "FOLLOW-UP:" in line.upper():
                current_section = "followup"
                follow_up_text = line.split(':', 1)[1].strip() if ':' in line else ""
                if follow_up_text:
                    follow_up_interval = follow_up_text
                    
            else:
                # Process content based on current section
                if current_section == "differential" and line.startswith("-"):
                    # Parse differential diagnosis
                    import re
                    match = re.search(r'([^(\d]+).*?(\d+(?:\.\d+)?)\s*%', line)
                    if match:
                        condition = match.group(1).strip().strip('-').strip()
                        probability = float(match.group(2)) / 100
                        differential_diagnoses.append(
                            DifferentialDiagnosis(
                                condition=condition,
                                probability=probability
                            )
                        )
                        
                elif current_section == "characteristics":
                    # Parse ABCDE characteristics
                    if not lesion_characteristics:
                        lesion_characteristics = LesionCharacteristics()
                    
                    line_lower = line.lower()
                    if "asymmetry" in line_lower:
                        match = re.search(r'(\d+(?:\.\d+)?)', line)
                        if match:
                            lesion_characteristics.asymmetry = float(match.group(1))
                    elif "border" in line_lower:
                        match = re.search(r'(\d+(?:\.\d+)?)', line)
                        if match:
                            lesion_characteristics.border_irregularity = float(match.group(1))
                    elif "color" in line_lower:
                        match = re.search(r'(\d+(?:\.\d+)?)', line)
                        if match:
                            lesion_characteristics.color_variation = float(match.group(1))
                    elif "diameter" in line_lower:
                        match = re.search(r'(\d+(?:\.\d+)?)\s*mm', line)
                        if match:
                            lesion_characteristics.diameter_mm = float(match.group(1))
                            
                elif current_section == "recommendations" and line.startswith("-"):
                    recommendations.append(line.strip("- "))
                    
                elif current_section == "risk" and line:
                    risk_assessment = f"{risk_assessment} {line}".strip()
        
        # Ensure we have at least some values
        if confidence == 0 and primary_diagnosis != "Analysis pending":
            confidence = 0.75  # Default confidence if not specified
            
        if not differential_diagnoses:
            # Add some default differential diagnoses
            differential_diagnoses = [
                DifferentialDiagnosis(
                    condition="Requires clinical correlation",
                    probability=0.1
                )
            ]
        
        # Create structured result
        return AnalysisResult(
            primary_diagnosis=primary_diagnosis,
            confidence=confidence,
            differential_diagnoses=differential_diagnoses,
            lesion_characteristics=lesion_characteristics,
            risk_assessment=risk_assessment,
            recommendations=recommendations,
            requires_biopsy=requires_biopsy,
            follow_up_interval=follow_up_interval
        )

# Singleton instance
_ai_engine: Optional[DermatologyAI] = None

def get_ai_engine() -> DermatologyAI:
    """Get or create the AI engine singleton"""
    global _ai_engine
    if _ai_engine is None:
        _ai_engine = DermatologyAI()
    return _ai_engine