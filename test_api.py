#!/usr/bin/env python3
"""
Test script for Ki Wellness AI Service API
"""

import requests
import json
import os
from dotenv import load_dotenv

def test_api_endpoints():
    """Test the API endpoints"""
    
    # Load environment variables
    load_dotenv()
    
    # Get API key from environment
    api_key = os.getenv('VALID_API_KEYS', 'ki-wellness-ai-service-key')
    if ',' in api_key:
        api_key = api_key.split(',')[0].strip()
    
    # Base URL - test both local and deployed
    base_urls = [
        'http://localhost:5001',  # Local
        'https://ki-ai-service.onrender.com'  # Deployed
    ]
    
    headers = {
        'X-API-Key': api_key,
        'Content-Type': 'application/json'
    }
    
    print(f"🔑 Using API key: {api_key}")
    print("=" * 50)
    
    for base_url in base_urls:
        print(f"\n🌐 Testing: {base_url}")
        print("-" * 30)
        
        # Test 1: Health endpoint (no API key required)
        try:
            response = requests.get(f"{base_url}/health", timeout=10)
            print(f"✅ Health endpoint: {response.status_code}")
            if response.status_code == 200:
                print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"❌ Health endpoint failed: {e}")
        
        # Test 2: Status endpoint (requires API key)
        try:
            response = requests.get(f"{base_url}/api/status", headers=headers, timeout=10)
            print(f"✅ Status endpoint: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Service: {data.get('service', 'N/A')}")
                print(f"   Status: {data.get('status', 'N/A')}")
                if 'components' in data:
                    print(f"   Ollama: {data['components'].get('ollama', 'N/A')}")
                    print(f"   Database: {data['components'].get('database', 'N/A')}")
        except Exception as e:
            print(f"❌ Status endpoint failed: {e}")
        
        # Test 3: Chat endpoint (requires API key) - Fixed URL
        try:
            chat_data = {
                "message": "Hello, how are you?",
                "user_id": "test_user"
            }
            response = requests.post(f"{base_url}/api/chat/message", 
                                   headers=headers, 
                                   json=chat_data, 
                                   timeout=30)
            print(f"✅ Chat endpoint: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   Response: {data.get('response', 'N/A')[:100]}...")
            elif response.status_code == 500:
                print(f"   Error: {response.text[:200]}...")
        except Exception as e:
            print(f"❌ Chat endpoint failed: {e}")
        
        # Test 4: Test without API key (should return 401)
        try:
            response = requests.get(f"{base_url}/api/status", timeout=10)
            print(f"✅ No API key test: {response.status_code} (expected 401)")
        except Exception as e:
            print(f"❌ No API key test failed: {e}")

if __name__ == "__main__":
    test_api_endpoints()
