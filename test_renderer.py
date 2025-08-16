#!/usr/bin/env python3
"""
Simple test script for the Playwright renderer
Run this after installing dependencies to verify everything works
"""

import requests
import json
import os

def test_renderer():
    """Test the renderer endpoint"""
    base_url = "http://127.0.0.1:5050"
    
    # Test data for the onepager template
    test_data = {
        "template": "onepager",
        "format": "png",
        "data": {
            "brand_slug": "demo",  # Use existing brand if available
            "title": "Test Renderer",
            "subtitle": "Verification Test",
            "cta": "Get Started"
        },
        "width": 1200,
        "height": 1600,
        "scale": 2
    }
    
    try:
        print("Testing renderer endpoint...")
        print(f"URL: {base_url}/render")
        print(f"Data: {json.dumps(test_data, indent=2)}")
        
        # Test PNG rendering
        response = requests.post(
            f"{base_url}/render",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ PNG rendering successful!")
            
            # Save the PNG file
            with open("test-output.png", "wb") as f:
                f.write(response.content)
            print("📁 Saved as test-output.png")
            
        else:
            print(f"❌ PNG rendering failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        # Test PDF rendering
        test_data["format"] = "pdf"
        response = requests.post(
            f"{base_url}/render",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("✅ PDF rendering successful!")
            
            # Save the PDF file
            with open("test-output.pdf", "wb") as f:
                f.write(response.content)
            print("📁 Saved as test-output.pdf")
            
        else:
            print(f"❌ PDF rendering failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
        # Test templates endpoint
        response = requests.get(f"{base_url}/templates")
        if response.status_code == 200:
            templates = response.json().get("templates", [])
            print(f"✅ Templates endpoint working: {templates}")
        else:
            print(f"❌ Templates endpoint failed: {response.status_code}")
            
        # Test health endpoint
        response = requests.get(f"{base_url}/healthz")
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            
        print("\n🎉 All tests passed! Renderer is working correctly.")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to Flask server")
        print("Make sure the server is running with: python -m app.main")
        return False
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Playwright Renderer")
    print("=" * 40)
    
    success = test_renderer()
    
    if success:
        print("\n✅ Renderer test completed successfully!")
        print("You can now use the renderer API to generate PNG and PDF assets.")
        print("\n💡 Try the new CLI command:")
        print("   python cli.py render <brand-slug> <template> --format png")
        print("   python cli.py render <brand-slug> <template> --format pdf")
    else:
        print("\n❌ Renderer test failed!")
        print("Check the error messages above and ensure all dependencies are installed.")
        print("\nSetup steps:")
        print("1. pip install -r requirements.txt")
        print("2. python -m playwright install chromium")
        print("3. python -m app.main")
        print("4. python test_renderer.py")
