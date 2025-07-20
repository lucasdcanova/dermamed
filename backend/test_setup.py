#!/usr/bin/env python3
"""Test script to verify DermaMed setup"""

import sys
import os

def test_imports():
    """Test all required imports"""
    print("Testing imports...")
    
    modules = [
        ("FastAPI", "fastapi"),
        ("PyTorch", "torch"),
        ("Transformers", "transformers"),
        ("PIL", "PIL"),
        ("OpenCV", "cv2"),
        ("SQLAlchemy", "sqlalchemy"),
        ("Pydantic", "pydantic")
    ]
    
    all_good = True
    for name, module in modules:
        try:
            __import__(module)
            print(f"✓ {name}")
        except ImportError:
            print(f"✗ {name} - Not installed")
            all_good = False
    
    return all_good

def test_gpu():
    """Test GPU availability"""
    print("\nTesting GPU...")
    try:
        import torch
        if torch.cuda.is_available():
            print(f"✓ GPU available: {torch.cuda.get_device_name(0)}")
            print(f"  CUDA version: {torch.version.cuda}")
        else:
            print("⚠ No GPU detected - will use CPU (slower)")
    except Exception as e:
        print(f"✗ GPU test failed: {e}")

def test_api():
    """Test if API can be imported"""
    print("\nTesting API structure...")
    try:
        from app.main import app
        from app.core.config import get_settings
        print("✓ API modules load correctly")
        
        settings = get_settings()
        print(f"✓ App name: {settings.app_name}")
        print(f"✓ Version: {settings.app_version}")
    except Exception as e:
        print(f"✗ API test failed: {e}")
        return False
    return True

def test_directories():
    """Test directory structure"""
    print("\nChecking directories...")
    dirs = ["models", "uploads", "logs", "data"]
    for dir_name in dirs:
        if os.path.exists(dir_name):
            print(f"✓ {dir_name}/")
        else:
            print(f"⚠ {dir_name}/ (will be created on startup)")

def main():
    """Run all tests"""
    print("🔍 DermaMed Setup Test\n")
    
    # Add current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Run tests
    imports_ok = test_imports()
    test_gpu()
    api_ok = test_api()
    test_directories()
    
    # Summary
    print("\n" + "="*50)
    if imports_ok and api_ok:
        print("✅ Setup looks good! You can start the server with:")
        print("   python run_dev.py")
    else:
        print("❌ Some issues found. Please check the errors above.")
        print("   Run: pip install -r requirements.txt")
    
    print("\n📝 Next steps:")
    print("1. Copy .env.example to .env and configure")
    print("2. Add your Hugging Face token for MedGemma")
    print("3. Run the development server")
    print("4. Access http://localhost:8000/docs")

if __name__ == "__main__":
    main()