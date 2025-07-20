#!/usr/bin/env python3
"""Test MedGemma API integration"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv
from huggingface_hub import InferenceClient

# Load environment variables
load_dotenv()

def test_basic_inference():
    """Test basic MedGemma inference with a sample image"""
    
    # Check if token is set
    token = os.getenv("HUGGINGFACE_TOKEN")
    if not token or token == "hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx":
        print("❌ Please set your Hugging Face token in .env file")
        print("   Get your token from: https://huggingface.co/settings/tokens")
        return False
    
    print("🔍 Testing MedGemma API connection...")
    
    try:
        # Initialize client
        client = InferenceClient(token=token)
        
        # Test with a public dermatology image
        completion = client.chat.completions.create(
            model="google/medgemma-4b-it",
            messages=[
                {
                    "role": "system",
                    "content": "You are a dermatology AI assistant. Analyze skin lesions professionally."
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this skin lesion. What type of lesion is this? Is it concerning?"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Melanoma.jpg/300px-Melanoma.jpg"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        print("✅ MedGemma API connection successful!")
        print("\n📋 Response:")
        print("-" * 50)
        print(completion.choices[0].message.content)
        print("-" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        
        if "401" in str(e):
            print("\n💡 Authentication error. Please check:")
            print("   1. Your token is valid")
            print("   2. You have accepted MedGemma terms at:")
            print("      https://huggingface.co/google/medgemma-4b-it")
        elif "model" in str(e).lower():
            print("\n💡 Model access error. Please:")
            print("   1. Visit https://huggingface.co/google/medgemma-4b-it")
            print("   2. Click 'Agree and access repository'")
            print("   3. Accept the terms of use")
        
        return False

def test_dermamed_integration():
    """Test DermaMed's AI engine integration"""
    
    print("\n🧪 Testing DermaMed integration...")
    
    try:
        from app.core.ai_engine_v2 import DermatologyAI
        
        # Initialize AI engine
        ai = DermatologyAI()
        print("✅ DermatologyAI initialized")
        
        # Test prompt building
        clinical_context = {
            "patient_age": 45,
            "patient_sex": "F",
            "lesion_location": "Upper back",
            "clinical_history": "New pigmented lesion noticed 3 months ago"
        }
        
        prompt = ai._build_analysis_prompt(clinical_context)
        print("\n📝 Generated prompt:")
        print("-" * 50)
        print(prompt[:200] + "...")
        print("-" * 50)
        
        print("\n✅ DermaMed integration test passed!")
        return True
        
    except Exception as e:
        print(f"❌ Integration error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 MedGemma API Integration Test\n")
    
    # Test basic inference
    inference_ok = test_basic_inference()
    
    # Test DermaMed integration
    integration_ok = test_dermamed_integration()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   Basic Inference: {'✅ Passed' if inference_ok else '❌ Failed'}")
    print(f"   DermaMed Integration: {'✅ Passed' if integration_ok else '❌ Failed'}")
    
    if inference_ok and integration_ok:
        print("\n🎉 All tests passed! MedGemma is ready to use.")
        print("\n📝 Next steps:")
        print("   1. Start the server: python run_dev.py")
        print("   2. Upload a dermatology image via API")
        print("   3. Get AI-powered analysis results")
    else:
        print("\n⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()