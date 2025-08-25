#!/usr/bin/env python3
"""
Test script to verify Ollama is working correctly
"""

import os
import ollama
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_ollama_connection():
    """Test Ollama connection and basic functionality"""
    print("🧪 Testing Ollama connection...")
    
    # Set Ollama host if specified
    ollama_base_url = os.getenv('OLLAMA_BASE_URL')
    if ollama_base_url:
        print(f"📍 Using Ollama at: {ollama_base_url}")
        ollama.set_host(ollama_base_url)
    else:
        print("📍 Using default Ollama at: http://localhost:11434")
    
    # Test basic connection
    try:
        print("🔍 Testing Ollama API connection...")
        response = ollama.chat(
            model=os.getenv('OLLAMA_MODEL', 'mistral'),
            messages=[{"role": "user", "content": "Say 'Hello, Ollama is working!'"}]
        )
        
        print("✅ Ollama connection successful!")
        print(f"🤖 Model: {os.getenv('OLLAMA_MODEL', 'mistral')}")
        print(f"💬 Response: {response['message']['content']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ollama connection failed: {e}")
        return False

def test_ollama_models():
    """Test listing available models"""
    try:
        print("\n📋 Testing model listing...")
        models = ollama.list()
        print("✅ Available models:")
        for model in models['models']:
            print(f"  - {model['name']} ({model['size']})")
        return True
    except Exception as e:
        print(f"❌ Failed to list models: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Ki AI Model - Ollama Test")
    print("=" * 40)
    
    # Test connection
    connection_ok = test_ollama_connection()
    
    # Test models if connection is ok
    if connection_ok:
        test_ollama_models()
    
    print("\n" + "=" * 40)
    if connection_ok:
        print("🎉 All tests passed! Ollama is working correctly.")
    else:
        print("💥 Some tests failed. Check Ollama installation and configuration.")
