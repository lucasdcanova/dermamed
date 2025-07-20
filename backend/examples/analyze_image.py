#!/usr/bin/env python3
"""
Example: Analyze a dermatological image using DermaMed API

This example shows how to:
1. Authenticate with the API
2. Upload an image for analysis
3. Get structured results
"""

import requests
import json
from pathlib import Path

# API configuration
API_URL = "http://localhost:8000"
USERNAME = "demo_doctor"
PASSWORD = "demo123"

def get_auth_token():
    """Get JWT authentication token"""
    response = requests.post(
        f"{API_URL}/api/v1/auth/token",
        data={
            "username": USERNAME,
            "password": PASSWORD
        }
    )
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"Authentication failed: {response.text}")

def analyze_image(image_path: str, token: str, clinical_data: dict = None):
    """Analyze a dermatological image"""
    
    # Prepare the request
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    files = {
        "file": open(image_path, "rb")
    }
    
    data = clinical_data or {}
    
    # Send request
    response = requests.post(
        f"{API_URL}/api/v1/analysis/",
        headers=headers,
        files=files,
        data=data
    )
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Analysis failed: {response.text}")

def main():
    """Main example flow"""
    
    print("🏥 DermaMed Image Analysis Example\n")
    
    # Step 1: Authenticate
    print("1. Authenticating...")
    try:
        token = get_auth_token()
        print("   ✅ Authentication successful")
    except Exception as e:
        print(f"   ❌ Authentication failed: {e}")
        return
    
    # Step 2: Prepare clinical data
    clinical_data = {
        "patient_age": 35,
        "patient_sex": "M",
        "lesion_location": "Left forearm",
        "clinical_history": "New mole appeared 6 months ago, has been growing",
        "symptoms_duration": "6 months"
    }
    
    # Step 3: Analyze image
    # Note: Replace with actual image path
    image_path = "sample_lesion.jpg"
    
    if not Path(image_path).exists():
        print("\n2. Demo mode (no image file)")
        # Use demo endpoint instead
        response = requests.post(f"{API_URL}/api/v1/analysis/demo")
        result = response.json()
    else:
        print(f"\n2. Analyzing image: {image_path}")
        try:
            result = analyze_image(image_path, token, clinical_data)
            print("   ✅ Analysis complete")
        except Exception as e:
            print(f"   ❌ Analysis failed: {e}")
            return
    
    # Step 4: Display results
    print("\n📊 Analysis Results:")
    print("-" * 60)
    
    if result.get("analysis"):
        analysis = result["analysis"]
        print(f"Primary Diagnosis: {analysis['primary_diagnosis']}")
        print(f"Confidence: {analysis['confidence'] * 100:.1f}%")
        print(f"Risk Assessment: {analysis['risk_assessment']}")
        print(f"Requires Biopsy: {'Yes' if analysis['requires_biopsy'] else 'No'}")
        
        print("\nDifferential Diagnoses:")
        for diff in analysis.get("differential_diagnoses", []):
            print(f"  - {diff['condition']}: {diff['probability'] * 100:.1f}%")
        
        print("\nRecommendations:")
        for rec in analysis.get("recommendations", []):
            print(f"  • {rec}")
        
        if analysis.get("lesion_characteristics"):
            chars = analysis["lesion_characteristics"]
            print("\nABCDE Assessment:")
            if chars.get("asymmetry") is not None:
                print(f"  - Asymmetry: {chars['asymmetry']:.2f}")
            if chars.get("border_irregularity") is not None:
                print(f"  - Border: {chars['border_irregularity']:.2f}")
            if chars.get("color_variation") is not None:
                print(f"  - Color: {chars['color_variation']:.2f}")
            if chars.get("diameter_mm") is not None:
                print(f"  - Diameter: {chars['diameter_mm']:.1f}mm")
    
    print("\n⚠️  Compliance:")
    print(f"   {result['compliance']['disclaimer'][:100]}...")
    
    print("-" * 60)

if __name__ == "__main__":
    main()