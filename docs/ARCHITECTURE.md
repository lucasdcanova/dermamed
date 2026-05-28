# DermaMed - Dermatological Analysis Software Architecture

> **Historical / aspirational design document.** This file was drafted during
> the initial scoping of DermaMed in mid-2025 and describes the *intended*
> shape of a hypothetical product, not what the code actually implements.
> Several sections (EHR integration, mobile app, Kubernetes, GCP, HIPAA/GDPR
> compliance, "Class II / IIa" classification) describe future-state work
> that **has not been performed and is not present in the codebase**. Treat
> this document as a developer's planning sketch.
>
> For the authoritative non-device statement, see
> [`DISCLAIMER.md`](DISCLAIMER.md). For the regulatory pathway analysis, see
> [`REGULATORY_POSITION.md`](REGULATORY_POSITION.md). For what is actually
> built today, see the project [`README.md`](../README.md) section
> "What works, what doesn't".
>
> Nothing in this document should be read as a regulatory claim, a clinical
> claim, or a representation that DermaMed is HIPAA-, GDPR-, or
> LGPD-compliant. It is not.

## Overview
DermaMed is a dermatological analysis **research prototype** that wires
Google's MedGemma 4B vision-language model into a FastAPI scaffold. The
original scoping document framed it as software "designed to assist
healthcare professionals" — that framing is aspirational only; in practice
the repository is research code with no clinical validation and no
regulatory pathway. See the banner above.

## Core Components

### 1. AI Model Integration
- **Model**: MedGemma 4B Multimodal (available on Hugging Face)
- **Image Encoder**: MedSigLIP (400M parameters)
- **Capabilities**: Skin lesion classification, melanoma detection, dermatological condition analysis

### 2. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (React/Next.js)                │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │Image Upload │  │Result Display│  │Patient History   │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │ REST API
┌───────────────────────────┴─────────────────────────────────┐
│                    Backend (Python/FastAPI)                  │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │API Endpoints│  │Authentication│  │Data Validation   │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└───────────────────────────┬─────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────┐
│                  AI Processing Pipeline                      │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │Preprocessing│  │MedGemma Model│  │Post-processing  │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │
┌───────────────────────────┴─────────────────────────────────┐
│                    Data Storage (PostgreSQL)                 │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │Patient Data │  │Analysis Logs │  │Image Storage    │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### 3. Key Features

#### Image Processing Pipeline
1. **Image Upload**: Support for JPG, PNG, DICOM formats
2. **Preprocessing**: 
   - Resize to model input dimensions
   - Normalization
   - Quality enhancement
   - ROI detection

#### AI Analysis
1. **Primary Analysis**: Skin condition classification
2. **Risk Assessment**: Melanoma probability scoring
3. **Feature Detection**: Lesion characteristics (ABCDE criteria)
4. **Differential Diagnosis**: Multiple condition probabilities

#### Safety & Compliance (aspirational — not implemented)
1. **Disclaimers**: present in the README and `DISCLAIMER.md`. Not surfaced
   inside the API response body.
2. **Professional Use**: original intent. The repository is **not**
   distributed for clinical use; see the banner at the top of this file.
3. **Audit Trail**: JSON-lines log file. **Not** tamper-evident, **not**
   compliance-grade. Placeholder for what an audit pipeline would look like.
4. **Data Privacy**: **No** HIPAA, GDPR, or LGPD controls are implemented.

### 4. Technology Stack

#### Backend
- **Framework**: FastAPI (Python)
- **AI Framework**: PyTorch/TensorFlow
- **Model Hosting**: Hugging Face Transformers
- **Image Processing**: OpenCV, Pillow
- **Database**: PostgreSQL
- **Cache**: Redis

#### Frontend
- **Framework**: Next.js 14
- **UI Library**: Material-UI / Shadcn
- **State Management**: Zustand
- **Image Viewer**: Cornerstone.js

#### Infrastructure
- **Container**: Docker
- **Orchestration**: Kubernetes
- **Cloud**: Google Cloud Platform (for Vertex AI integration)
- **Storage**: Google Cloud Storage for images
- **Monitoring**: Prometheus + Grafana

### 5. Implementation Phases

#### Phase 1: MVP (Months 1-2)
- Basic image upload and analysis
- MedGemma integration
- Simple result display
- Essential safety disclaimers

#### Phase 2: Enhanced Features (Months 3-4)
- Multiple image comparison
- Historical tracking
- Advanced preprocessing
- Detailed reporting

#### Phase 3: Clinical Integration (Months 5-6)
- EHR integration
- Multi-user support
- Advanced analytics
- Mobile app

### 6. Regulatory Considerations (aspirational — not implemented)

The original scoping listed the following as items that *would* apply if the
project were ever advanced into a product. None of them are met today.

1. **Hypothetical classification** (not the current status): would likely
   be FDA Class II SaMD / EU MDR Class IIb under Rule 11 (melanoma is
   potentially fatal) / ANVISA Classe II under RDC 657/2022. **Current
   status: none of these. Not a device.**
2. **Clinical validation:** required before any medical use — **not
   performed**.
3. **Quality management (ISO 13485):** would be required — **not
   implemented**.
4. **Data protection (HIPAA / GDPR / LGPD):** would be required — **not
   implemented**. No BAA, no DPA, no DPIA, no LIA, no ROPA.

See [`REGULATORY_POSITION.md`](REGULATORY_POSITION.md) for the full
per-jurisdiction analysis.

### 7. Model Integration Details

```python
# Example MedGemma Integration
from transformers import AutoModel, AutoTokenizer
import torch

class DermatologyAnalyzer:
    def __init__(self):
        self.model = AutoModel.from_pretrained("google/medgemma-4b-it")
        self.tokenizer = AutoTokenizer.from_pretrained("google/medgemma-4b-it")
        
    def analyze_skin_image(self, image_path, clinical_notes=""):
        # Preprocess image
        processed_image = self.preprocess_image(image_path)
        
        # Prepare multimodal input
        inputs = self.tokenizer(
            text=f"Analyze this dermatological image. Clinical notes: {clinical_notes}",
            images=processed_image,
            return_tensors="pt"
        )
        
        # Generate analysis
        with torch.no_grad():
            outputs = self.model.generate(**inputs)
            
        # Decode results
        analysis = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        return self.parse_medical_analysis(analysis)
```

### 8. Security Measures

1. **Authentication**: OAuth 2.0 / SAML for healthcare providers
2. **Encryption**: TLS 1.3 for transit, AES-256 for storage
3. **Access Control**: Role-based permissions
4. **Audit Logging**: Comprehensive activity tracking
5. **Data Anonymization**: Remove PII from training data

### 9. Performance Requirements

- **Image Analysis Time**: < 5 seconds
- **Concurrent Users**: 100+
- **Uptime**: 99.9%
- **Image Size**: Up to 50MB
- **Storage**: 1TB+ for image archive

### 10. Development Roadmap

1. **Week 1-2**: Environment setup, MedGemma access
2. **Week 3-4**: Basic API and model integration
3. **Week 5-6**: Frontend development
4. **Week 7-8**: Testing and validation
5. **Week 9-10**: Security and compliance
6. **Week 11-12**: Deployment and documentation