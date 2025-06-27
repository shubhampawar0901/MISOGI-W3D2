#!/usr/bin/env python3
"""
Test script for the Multimodal QA API with example image-question pairs.
"""

import requests
import json
import time
from pathlib import Path

# API base URL
BASE_URL = "http://localhost:8000"

# Test image URLs (publicly accessible images)
TEST_IMAGES = [
    {
        "url": "https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=800",
        "question": "What time of day does this landscape photo appear to be taken?",
        "description": "Mountain landscape at sunset"
    },
    {
        "url": "https://images.unsplash.com/photo-1565299624946-b28f40a0ca4b?w=800",
        "question": "What ingredients can you identify in this food image?",
        "description": "Pizza with various toppings"
    },
    {
        "url": "https://images.unsplash.com/photo-1518717758536-85ae29035b6d?w=800",
        "question": "What animals do you see and what are they doing?",
        "description": "Dogs playing in a park"
    }
]

def test_api_status():
    """Test if the API is running and check model status."""
    print("🔍 Testing API Status...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✓ API is running")
            
            # Check model status
            status_response = requests.get(f"{BASE_URL}/status")
            if status_response.status_code == 200:
                status = status_response.json()
                print(f"✓ Vision models available: {status['vision_models_available']}")
                print(f"✓ Fallback models available: {status['fallback_models_available']}")
                print(f"✓ OpenAI configured: {status['openai_configured']}")
                print(f"✓ Anthropic configured: {status['anthropic_configured']}")
                return True
            else:
                print("❌ Could not get model status")
                return False
        else:
            print("❌ API is not responding")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API. Make sure the backend is running on port 8000")
        return False

def test_image_analysis(image_data, test_number):
    """Test image analysis with a specific image-question pair."""
    print(f"\n📸 Test {test_number}: {image_data['description']}")
    print(f"Question: {image_data['question']}")
    print(f"Image URL: {image_data['url']}")
    
    start_time = time.time()
    
    try:
        response = requests.post(
            f"{BASE_URL}/analyze-url",
            json={
                "question": image_data["question"],
                "image_url": image_data["url"]
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            processing_time = time.time() - start_time
            
            print(f"✓ Analysis completed in {processing_time:.2f}s")
            print(f"Model used: {result['model_used']}")
            print(f"Processing time (server): {result['processing_time']:.2f}s")
            print(f"Fallback used: {result['fallback_used']}")
            print(f"Answer: {result['answer'][:200]}{'...' if len(result['answer']) > 200 else ''}")
            
            return {
                "success": True,
                "model": result['model_used'],
                "processing_time": result['processing_time'],
                "fallback_used": result['fallback_used'],
                "answer_length": len(result['answer'])
            }
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"Error details: {response.text}")
            return {"success": False, "error": response.text}
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return {"success": False, "error": "timeout"}
    except Exception as e:
        print(f"❌ Error: {e}")
        return {"success": False, "error": str(e)}

def generate_test_report(results):
    """Generate a summary report of test results."""
    print("\n" + "="*60)
    print("📊 TEST REPORT SUMMARY")
    print("="*60)
    
    successful_tests = [r for r in results if r["success"]]
    failed_tests = [r for r in results if not r["success"]]
    
    print(f"Total tests: {len(results)}")
    print(f"Successful: {len(successful_tests)}")
    print(f"Failed: {len(failed_tests)}")
    
    if successful_tests:
        print(f"\n✅ Successful Tests:")
        models_used = {}
        total_processing_time = 0
        fallback_count = 0
        
        for i, result in enumerate(successful_tests, 1):
            model = result["model"]
            models_used[model] = models_used.get(model, 0) + 1
            total_processing_time += result["processing_time"]
            if result["fallback_used"]:
                fallback_count += 1
            
            print(f"  Test {i}: {model} ({result['processing_time']:.2f}s)")
        
        print(f"\n📈 Performance Metrics:")
        print(f"  Average processing time: {total_processing_time/len(successful_tests):.2f}s")
        print(f"  Fallback usage: {fallback_count}/{len(successful_tests)} tests")
        
        print(f"\n🤖 Models Used:")
        for model, count in models_used.items():
            print(f"  {model}: {count} times")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for i, result in enumerate(failed_tests, 1):
            print(f"  Test {i}: {result['error']}")
    
    print("\n" + "="*60)

def main():
    """Main test function."""
    print("🧪 Multimodal QA API Test Suite")
    print("="*40)
    
    # Test API status first
    if not test_api_status():
        print("\n❌ API tests failed. Please ensure:")
        print("1. Backend server is running (python start_backend.py)")
        print("2. At least one API key is configured in .env")
        print("3. Server is accessible on http://localhost:8000")
        return
    
    # Run image analysis tests
    results = []
    for i, image_data in enumerate(TEST_IMAGES, 1):
        result = test_image_analysis(image_data, i)
        results.append(result)
        
        # Small delay between requests
        time.sleep(1)
    
    # Generate report
    generate_test_report(results)
    
    print(f"\n🎯 Test completed! Check the results above.")
    print(f"💡 You can also test the web interface at http://localhost:3000")

if __name__ == "__main__":
    main()
