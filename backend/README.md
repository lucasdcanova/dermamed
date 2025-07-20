# DermaMed Backend

AI-powered dermatological analysis system using Google's MedGemma model.

## Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows

# Install requirements
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings:
# - Add your Hugging Face token for MedGemma access
# - Update database credentials
# - Set secret keys
```

### 3. Run Development Server

```bash
# Using the helper script
python run_dev.py

# Or directly with uvicorn
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## API Documentation

Once running, access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Default Credentials

For testing:
- Username: `demo_doctor`
- Password: `demo123`

## Key Endpoints

### Authentication
- `POST /api/v1/auth/token` - Login and get JWT token
- `POST /api/v1/auth/register` - Register new medical professional
- `GET /api/v1/auth/me` - Get current user info

### Analysis
- `POST /api/v1/analysis/` - Analyze dermatological image
- `GET /api/v1/analysis/{id}` - Get analysis results
- `POST /api/v1/analysis/demo` - Demo analysis (no auth required)

## MedGemma Integration

### Prerequisites
1. Create a Hugging Face account
2. Request access to `google/medgemma-4b-it`
3. Generate an access token
4. Add token to `.env` file

### Model Download
The model will be automatically downloaded on first use and cached locally.

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html
```

## Docker Deployment

```bash
# Build image
docker build -t dermamed-backend .

# Run container
docker run -p 8000:8000 --env-file .env dermamed-backend
```

## Security Notes

- All endpoints except `/health` and `/api/v1/analysis/demo` require authentication
- Medical data is logged separately for HIPAA compliance
- All analyses include mandatory disclaimers
- Not approved for diagnostic use without proper validation

## Troubleshooting

### Model Loading Issues
- Ensure you have sufficient RAM (32GB+ recommended)
- For GPU support, ensure CUDA is properly installed
- Check Hugging Face token is valid

### Import Errors
- Run `pip install -r requirements.txt` again
- Ensure Python 3.9+ is being used

### Database Connection
- Check PostgreSQL is running
- Verify credentials in `.env`