import torch
from transformers import AutoModel, AutoTokenizer, AutoProcessor
from PIL import Image
import numpy as np
from typing import Dict, Any, Optional, Tuple
import logging
import os
from functools import lru_cache
import time

from app.core.config import get_settings, MEDICAL_DISCLAIMER
from app.schemas.analysis import (
    AnalysisResult, 
    DifferentialDiagnosis, 
    LesionCharacteristics
)

logger = logging.getLogger(__name__)
settings = get_settings()

class DermatologyAI:
    """AI engine for dermatological image analysis using MedGemma"""
    
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.processor = None
        self.tokenizer = None
        self._initialized = False
        
        logger.info(f"DermatologyAI initialized with device: {self.device}")
        
    @lru_cache(maxsize=1)
    def initialize_model(self):
        """Load the MedGemma model (lazy loading)"""
        if self._initialized:
            return
            
        try:
            logger.info(f"Loading model: {settings.model_name}")
            
            # For MedGemma, we'll use the appropriate loading method
            # Note: Actual implementation depends on MedGemma's release format
            model_path = os.path.join(settings.model_cache_dir, "medgemma")
            
            if os.path.exists(model_path):
                # Load from cache
                self.model = AutoModel.from_pretrained(model_path)
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            else:
                # Download from Hugging Face
                self.model = AutoModel.from_pretrained(
                    settings.model_name,
                    use_auth_token=settings.huggingface_token if settings.huggingface_token else None
                )
                self.tokenizer = AutoTokenizer.from_pretrained(
                    settings.model_name,
                    use_auth_token=settings.huggingface_token if settings.huggingface_token else None
                )
                
                # Save to cache
                os.makedirs(model_path, exist_ok=True)
                self.model.save_pretrained(model_path)
                self.tokenizer.save_pretrained(model_path)
            
            self.model.to(self.device)
            self.model.eval()
            self._initialized = True
            
            logger.info("Model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise RuntimeError(f"Model initialization failed: {str(e)}")
    
    def preprocess_image(self, image_path: str) -> Tuple[torch.Tensor, Dict[str, int]]:
        """Preprocess dermatological image for analysis"""
        try:
            # Open and convert image
            image = Image.open(image_path).convert('RGB')
            original_size = image.size
            
            # Resize to model's expected dimensions (typically 224x224 or 512x512)
            target_size = (224, 224)  # Adjust based on MedGemma requirements
            image = image.resize(target_size, Image.Resampling.LANCZOS)
            
            # Convert to tensor and normalize
            image_array = np.array(image).astype(np.float32) / 255.0
            
            # Normalize with ImageNet stats (adjust if MedGemma uses different normalization)
            mean = np.array([0.485, 0.456, 0.406])
            std = np.array([0.229, 0.224, 0.225])
            image_array = (image_array - mean) / std
            
            # Convert to tensor
            image_tensor = torch.from_numpy(image_array).float()
            image_tensor = image_tensor.permute(2, 0, 1)  # HWC to CHW
            image_tensor = image_tensor.unsqueeze(0).to(self.device)
            
            metadata = {
                "original_width": original_size[0],
                "original_height": original_size[1],
                "processed_width": target_size[0],
                "processed_height": target_size[1]
            }
            
            return image_tensor, metadata
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {str(e)}")
            raise ValueError(f"Failed to process image: {str(e)}")
    
    def analyze(self, image_path: str, clinical_context: Optional[Dict[str, Any]] = None) -> AnalysisResult:
        """Perform dermatological analysis on an image"""
        
        # Ensure model is loaded
        self.initialize_model()
        
        start_time = time.time()
        
        try:
            # Preprocess image
            image_tensor, image_metadata = self.preprocess_image(image_path)
            
            # Prepare text prompt with clinical context
            prompt = self._build_analysis_prompt(clinical_context)
            
            # Tokenize prompt
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=512
            ).to(self.device)
            
            # Run inference
            with torch.no_grad():
                # For multimodal model, we'd pass both image and text
                # The exact API depends on MedGemma's implementation
                outputs = self.model.generate(
                    input_ids=inputs.input_ids,
                    attention_mask=inputs.attention_mask,
                    images=image_tensor,  # This depends on model's API
                    max_length=1024,
                    temperature=0.7,
                    do_sample=True,
                    top_p=0.9
                )
            
            # Decode response
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
            
            # Parse the model's response into structured format
            analysis_result = self._parse_model_response(response)
            
            # Add processing metadata
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
            "You are analyzing a dermatological image. Please provide a comprehensive analysis including:",
            "1. Primary diagnosis with confidence level",
            "2. Differential diagnoses with probabilities",
            "3. ABCDE criteria assessment if applicable",
            "4. Risk assessment and urgency level",
            "5. Recommended next steps and follow-up"
        ]
        
        if clinical_context:
            prompt_parts.append("\nClinical Context:")
            if clinical_context.get("clinical_history"):
                prompt_parts.append(f"History: {clinical_context['clinical_history']}")
            if clinical_context.get("patient_age"):
                prompt_parts.append(f"Age: {clinical_context['patient_age']}")
            if clinical_context.get("patient_sex"):
                prompt_parts.append(f"Sex: {clinical_context['patient_sex']}")
            if clinical_context.get("lesion_location"):
                prompt_parts.append(f"Location: {clinical_context['lesion_location']}")
            if clinical_context.get("symptoms_duration"):
                prompt_parts.append(f"Duration: {clinical_context['symptoms_duration']}")
        
        prompt_parts.append(
            "\nIMPORTANT: This analysis is for clinical decision support only. "
            "Format your response as a structured medical report."
        )
        
        return "\n".join(prompt_parts)
    
    def _parse_model_response(self, response: str) -> AnalysisResult:
        """Parse the model's text response into structured format"""
        
        # This is a simplified parser - in production, you'd use more sophisticated NLP
        # or require the model to output in a specific format (e.g., JSON)
        
        # Default values
        primary_diagnosis = "Analysis pending"
        confidence = 0.0
        differential_diagnoses = []
        risk_assessment = "Requires clinical correlation"
        recommendations = ["Professional medical evaluation recommended"]
        requires_biopsy = False
        
        # Simple parsing logic (would be more sophisticated in production)
        lines = response.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            
            if "primary diagnosis:" in line_lower or "diagnosis:" in line_lower:
                primary_diagnosis = line.split(':', 1)[1].strip()
            elif "confidence:" in line_lower:
                try:
                    confidence = float(line.split(':')[1].strip().replace('%', '')) / 100
                except:
                    confidence = 0.5
            elif "risk:" in line_lower:
                risk_assessment = line.split(':', 1)[1].strip()
            elif "recommend" in line_lower:
                recommendations.append(line.strip())
            elif "biopsy" in line_lower and ("recommend" in line_lower or "required" in line_lower):
                requires_biopsy = True
        
        # Create structured result
        return AnalysisResult(
            primary_diagnosis=primary_diagnosis,
            confidence=confidence,
            differential_diagnoses=differential_diagnoses,
            lesion_characteristics=None,  # Would be extracted from response
            risk_assessment=risk_assessment,
            recommendations=recommendations,
            requires_biopsy=requires_biopsy,
            follow_up_interval="As clinically indicated"
        )

# Singleton instance
_ai_engine: Optional[DermatologyAI] = None

def get_ai_engine() -> DermatologyAI:
    """Get or create the AI engine singleton"""
    global _ai_engine
    if _ai_engine is None:
        _ai_engine = DermatologyAI()
    return _ai_engine