# DermaMed - AI-Powered Dermatological Analysis System

## ⚠️ Important Disclaimer

This software is intended for use by qualified healthcare professionals as a clinical decision support tool only. It is NOT approved for diagnostic use and should not replace professional medical judgment.

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose (optional)
- NVIDIA GPU with CUDA support (recommended)
- Hugging Face account with MedGemma access

### Option 1: Local Development

```bash
# Install dependencies
make install

# Configure environment
cd backend
cp .env.example .env
# Edit .env with your settings

# Run the backend
make run-backend
```

### Option 2: Docker Deployment

```bash
# Start all services
make docker-up

# Stop services
make docker-down
```

## 📚 Documentation

- **Architecture**: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
- **Implementation Guide**: [docs/IMPLEMENTATION_GUIDE.md](docs/IMPLEMENTATION_GUIDE.md)
- **API Documentation**: http://localhost:8000/docs (when running)

## 🏗️ Project Structure

```
DermaMed/
├── backend/              # FastAPI backend application
│   ├── app/             # Application code
│   │   ├── api/         # API endpoints
│   │   ├── core/        # Core functionality (AI engine, config)
│   │   ├── models/      # Database models
│   │   └── schemas/     # Pydantic schemas
│   ├── tests/           # Test suite
│   └── requirements.txt # Python dependencies
├── frontend/            # Next.js frontend (to be implemented)
├── models/              # AI model storage
├── docs/                # Documentation
└── docker-compose.yml   # Docker services configuration
```

## 🔑 Key Features

- **AI-Powered Analysis**: Uses Google's MedGemma model trained on dermatological data
- **ABCDE Assessment**: Automated evaluation of lesion characteristics
- **Differential Diagnosis**: Multiple condition probabilities
- **Risk Stratification**: Urgency and follow-up recommendations
- **Compliance Ready**: Built-in disclaimers and audit logging
- **Secure**: JWT authentication, encrypted storage, HIPAA considerations

## 🧪 Testing

### Demo Credentials
- Username: `demo_doctor`
- Password: `demo123`

### Run Tests
```bash
cd backend
pytest
```

### Test Analysis Endpoint
```bash
# Get auth token
curl -X POST http://localhost:8000/api/v1/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=demo_doctor&password=demo123"

# Use demo endpoint (no auth required)
curl -X POST http://localhost:8000/api/v1/analysis/demo
```

## 📊 MedGemma Integration

### Getting Access
1. Create account at [Hugging Face](https://huggingface.co)
2. Request access to `google/medgemma-4b-it`
3. Generate access token
4. Add to `.env` file

### Model Details
- **Base Model**: MedGemma 4B Multimodal
- **Training Data**: Dermatology images, clinical cases
- **Capabilities**: Lesion classification, melanoma detection
- **Limitations**: Research use, requires validation

## 🔒 Security & Compliance

- **Authentication**: JWT-based auth for all endpoints
- **Data Privacy**: No patient data stored without encryption
- **Audit Logging**: All analyses logged for compliance
- **Medical Disclaimer**: Displayed on all results

## 🚧 Roadmap

- [x] Backend API implementation
- [x] MedGemma integration design
- [x] Authentication system
- [x] Compliance framework
- [ ] Frontend UI development
- [ ] Database persistence
- [ ] Real model integration
- [ ] Clinical validation
- [ ] Mobile application
- [ ] EHR integration

---

**Remember**: This tool is for clinical decision support only. Always rely on professional medical judgment for patient care decisions.