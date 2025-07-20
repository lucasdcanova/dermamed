# DermaMed Implementation Guide

## Getting Started with MedGemma

### 1. Accessing MedGemma

MedGemma is available through:
- **Hugging Face**: `google/medgemma-4b-it` 
- **License**: Permits research and commercial use (with restrictions)
- **Requirements**: No direct clinical use without validation

### 2. Prerequisites

```bash
# Python 3.9+
python --version

# CUDA 11.8+ (for GPU acceleration)
nvidia-smi

# System requirements
# - RAM: 32GB minimum
# - GPU: NVIDIA GPU with 16GB+ VRAM (recommended)
# - Storage: 100GB+ for models and data
```

### 3. Initial Setup

```bash
# Create project structure
mkdir -p DermaMed/{backend,frontend,models,data,docs}
cd DermaMed

# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install core dependencies
pip install torch torchvision transformers
pip install fastapi uvicorn python-multipart
pip install opencv-python pillow numpy
pip install sqlalchemy psycopg2-binary
pip install python-jose[cryptography] passlib[bcrypt]
```

### 4. MedGemma API Setup

Com a nova abordagem usando a API de inferência do Hugging Face, não é necessário baixar o modelo localmente. O MedGemma é acessado via API:

```python
# Exemplo de uso da API
from huggingface_hub import InferenceClient

client = InferenceClient(token=os.getenv("HUGGINGFACE_TOKEN"))

completion = client.chat.completions.create(
    model="google/medgemma-4b-it",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "Analyze this skin lesion"},
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64,..."}}
            ]
        }
    ]
)
```

**Vantagens da API:**
- Sem download de modelos grandes (8GB+)
- Início instantâneo
- Sempre usa a versão mais recente
- Menor uso de recursos locais

### 5. Core Implementation Structure

```
DermaMed/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI app
│   │   ├── models/           # Database models
│   │   ├── schemas/          # Pydantic schemas
│   │   ├── api/              # API endpoints
│   │   ├── core/             # Core functionality
│   │   │   ├── ai_engine.py  # MedGemma integration
│   │   │   ├── preprocessing.py
│   │   │   └── analysis.py
│   │   └── utils/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── components/
│   ├── pages/
│   ├── public/
│   └── package.json
└── docker-compose.yml
```

### 6. Basic AI Engine Implementation

```python
# backend/app/core/ai_engine.py
import torch
from transformers import AutoModel, AutoTokenizer
from PIL import Image
import numpy as np
from typing import Dict, Any

class DermatologyAI:
    def __init__(self, model_path: str = "./models/medgemma"):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = AutoModel.from_pretrained(model_path).to(self.device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model.eval()
    
    def preprocess_image(self, image_path: str) -> torch.Tensor:
        """Preprocess dermatological image for analysis"""
        image = Image.open(image_path).convert('RGB')
        
        # Resize to model's expected dimensions
        image = image.resize((224, 224))
        
        # Convert to tensor and normalize
        image_array = np.array(image) / 255.0
        image_tensor = torch.from_numpy(image_array).float()
        image_tensor = image_tensor.permute(2, 0, 1)  # CHW format
        
        return image_tensor.unsqueeze(0).to(self.device)
    
    def analyze(self, image_path: str, clinical_context: str = "") -> Dict[str, Any]:
        """Perform dermatological analysis"""
        # Preprocess image
        image_tensor = self.preprocess_image(image_path)
        
        # Prepare prompt
        prompt = f"""Analyze this dermatological image and provide:
        1. Primary diagnosis probability
        2. Differential diagnoses
        3. Lesion characteristics (ABCDE criteria if applicable)
        4. Recommended follow-up
        
        Clinical context: {clinical_context}
        
        IMPORTANT: This is for clinical decision support only."""
        
        # Tokenize input
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            padding=True,
            truncation=True
        ).to(self.device)
        
        # Generate analysis
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=512,
                temperature=0.7,
                do_sample=True
            )
        
        # Decode response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Parse and structure the response
        return self._parse_analysis(response)
    
    def _parse_analysis(self, raw_response: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        # This is a simplified parser - implement based on actual model output
        return {
            "status": "success",
            "analysis": {
                "primary_diagnosis": "Extracted from response",
                "confidence": 0.85,
                "differential_diagnoses": [],
                "characteristics": {},
                "recommendations": "Extracted recommendations",
                "disclaimer": "This analysis is for clinical decision support only and should not replace professional medical judgment."
            },
            "raw_response": raw_response
        }
```

### 7. API Implementation

```python
# backend/app/api/analysis.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Dict, Any
import tempfile
import os

from ..core.ai_engine import DermatologyAI
from ..schemas.analysis import AnalysisRequest, AnalysisResponse

router = APIRouter()
ai_engine = DermatologyAI()

@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...),
    clinical_notes: str = ""
) -> Dict[str, Any]:
    """Analyze dermatological image"""
    
    # Validate file type
    if not file.content_type.startswith('image/'):
        raise HTTPException(400, "File must be an image")
    
    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        # Perform analysis
        result = ai_engine.analyze(tmp_path, clinical_notes)
        
        # Add metadata
        result["metadata"] = {
            "filename": file.filename,
            "size": len(content),
            "content_type": file.content_type
        }
        
        return result
        
    finally:
        # Clean up
        os.unlink(tmp_path)
```

### 8. Frontend Implementation (Next.js)

```typescript
// frontend/components/ImageAnalyzer.tsx
import React, { useState } from 'react';
import { Button, Card, Upload, Spin, Alert } from 'antd';

interface AnalysisResult {
  analysis: {
    primary_diagnosis: string;
    confidence: number;
    differential_diagnoses: string[];
    recommendations: string;
    disclaimer: string;
  };
}

export const ImageAnalyzer: React.FC = () => {
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [imageUrl, setImageUrl] = useState<string>('');

  const handleUpload = async (file: File) => {
    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) throw new Error('Analysis failed');
      
      const data = await response.json();
      setResult(data);
      setImageUrl(URL.createObjectURL(file));
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="analyzer-container">
      <Card title="Dermatological Analysis">
        <Upload
          accept="image/*"
          showUploadList={false}
          beforeUpload={(file) => {
            handleUpload(file);
            return false;
          }}
        >
          <Button loading={uploading}>
            Upload Skin Image
          </Button>
        </Upload>

        {imageUrl && (
          <div className="image-preview">
            <img src={imageUrl} alt="Uploaded" style={{ maxWidth: '100%' }} />
          </div>
        )}

        {result && (
          <div className="results">
            <Alert
              message="Medical Disclaimer"
              description={result.analysis.disclaimer}
              type="warning"
              showIcon
            />
            
            <Card title="Analysis Results" style={{ marginTop: 16 }}>
              <p><strong>Primary Diagnosis:</strong> {result.analysis.primary_diagnosis}</p>
              <p><strong>Confidence:</strong> {(result.analysis.confidence * 100).toFixed(1)}%</p>
              <p><strong>Recommendations:</strong> {result.analysis.recommendations}</p>
            </Card>
          </div>
        )}
      </Card>
    </div>
  );
};
```

### 9. Deployment Configuration

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/dermamed
      - MODEL_PATH=/app/models/medgemma
    volumes:
      - ./models:/app/models
    depends_on:
      - db
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=dermamed
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 10. Important Considerations

#### Regulatory Compliance
```python
# backend/app/core/compliance.py
MEDICAL_DISCLAIMER = """
This AI-powered analysis is intended for use by qualified healthcare 
professionals as a clinical decision support tool only. It should not 
be used as the sole basis for diagnosis or treatment decisions. Always 
consult with appropriate medical professionals and consider the full 
clinical context when making medical decisions.

This software is not FDA-approved for diagnostic use.
"""

def add_compliance_headers(response: dict) -> dict:
    """Add required compliance information to all responses"""
    response["compliance"] = {
        "disclaimer": MEDICAL_DISCLAIMER,
        "intended_use": "Clinical decision support only",
        "regulatory_status": "Not approved for diagnostic use",
        "version": "1.0.0",
        "last_updated": "2025-01-13"
    }
    return response
```

### 11. Testing Framework

```python
# tests/test_analysis.py
import pytest
from app.core.ai_engine import DermatologyAI

def test_image_preprocessing():
    """Test image preprocessing pipeline"""
    ai = DermatologyAI()
    test_image = "tests/fixtures/sample_lesion.jpg"
    
    tensor = ai.preprocess_image(test_image)
    assert tensor.shape == (1, 3, 224, 224)
    assert tensor.dtype == torch.float32

def test_analysis_output_structure():
    """Test that analysis returns expected structure"""
    ai = DermatologyAI()
    result = ai.analyze("tests/fixtures/sample_lesion.jpg")
    
    assert "analysis" in result
    assert "primary_diagnosis" in result["analysis"]
    assert "confidence" in result["analysis"]
    assert "disclaimer" in result["analysis"]
```

### 12. Next Steps

1. **Obtain MedGemma Access**: Sign up on Hugging Face and accept model license
2. **Set Up Development Environment**: Follow the setup instructions above
3. **Implement MVP**: Start with basic image upload and analysis
4. **Add Safety Features**: Implement all required disclaimers and logging
5. **Validate Results**: Test with known dermatological cases
6. **Security Audit**: Ensure HIPAA/GDPR compliance
7. **Clinical Validation**: Partner with dermatologists for testing
8. **Regulatory Submission**: Prepare documentation for medical device approval