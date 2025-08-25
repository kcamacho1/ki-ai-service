#!/usr/bin/env python3
"""
Ollama Progress Monitor
Monitors model download progress with detailed logging and progress bars
"""

import os
import time
import json
import requests
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class OllamaProgressMonitor:
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.start_time = None
        
    def check_ollama_status(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def get_model_info(self, model_name: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific model"""
        try:
            response = requests.get(f"{self.base_url}/api/show", params={"name": model_name})
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return None
    
    def list_models(self) -> list:
        """List all available models"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return response.json().get("models", [])
        except:
            pass
        return []
    
    def monitor_pull_progress(self, model_name: str) -> bool:
        """Monitor model pull progress with detailed logging"""
        print(f"🚀 Starting download of {model_name} model...")
        self.start_time = datetime.now()
        
        # Check if model already exists
        existing_models = self.list_models()
        if any(model["name"] == model_name for model in existing_models):
            print(f"✅ Model {model_name} is already available")
            return True
        
        print("⏳ Initializing download...")
        print("📊 Progress will be displayed below:")
        print("-" * 60)
        
        try:
            # Start the pull process
            process = subprocess.Popen(
                ["ollama", "pull", model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            last_progress = ""
            download_started = False
            
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                
                if output:
                    line = output.strip()
                    
                    # Parse different types of progress messages
                    if "pulling" in line.lower():
                        print(f"📥 {line}")
                        download_started = True
                    elif "downloading" in line.lower():
                        print(f"⬇️  {line}")
                    elif "verifying" in line.lower():
                        print(f"🔍 {line}")
                    elif "writing" in line.lower():
                        print(f"💾 {line}")
                    elif "success" in line.lower():
                        print(f"✅ {line}")
                    elif "error" in line.lower():
                        print(f"❌ {line}")
                        return False
                    elif "already exists" in line.lower():
                        print(f"✅ {line}")
                    elif line and line != last_progress:
                        # Show other progress information
                        if download_started:
                            elapsed = datetime.now() - self.start_time
                            print(f"⏱️  [{elapsed}] {line}")
                        else:
                            print(f"ℹ️  {line}")
                        last_progress = line
            
            # Wait for process to complete
            return_code = process.poll()
            
            if return_code == 0:
                elapsed = datetime.now() - self.start_time
                print("-" * 60)
                print(f"🎉 Download completed successfully in {elapsed}")
                
                # Verify model is now available
                if self.get_model_info(model_name):
                    print(f"✅ Model {model_name} is now available for use")
                    return True
                else:
                    print(f"❌ Model {model_name} download may have failed")
                    return False
            else:
                print(f"❌ Download failed with return code {return_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error during download: {e}")
            return False
    
    def show_model_status(self, model_name: str):
        """Show detailed status of a model"""
        model_info = self.get_model_info(model_name)
        if model_info:
            print(f"📋 Model: {model_name}")
            print(f"📏 Size: {model_info.get('size', 'Unknown')}")
            print(f"📅 Modified: {model_info.get('modified_at', 'Unknown')}")
            print(f"🏷️  Tags: {', '.join(model_info.get('tags', []))}")
        else:
            print(f"❌ Model {model_name} not found")
    
    def run_health_check(self):
        """Run a comprehensive health check"""
        print("🏥 Running Ollama Health Check...")
        print("=" * 50)
        
        # Check if Ollama is running
        if self.check_ollama_status():
            print("✅ Ollama service is running and accessible")
        else:
            print("❌ Ollama service is not accessible")
            return False
        
        # List available models
        models = self.list_models()
        if models:
            print(f"📚 Found {len(models)} model(s):")
            for model in models:
                print(f"  - {model['name']} ({model.get('size', 'Unknown size')})")
        else:
            print("📚 No models found")
        
        # Check specific model
        target_model = os.getenv('OLLAMA_MODEL', 'mistral')
        print(f"\n🎯 Checking target model: {target_model}")
        self.show_model_status(target_model)
        
        return True

def main():
    """Main function to run the progress monitor"""
    print("🤖 Ollama Progress Monitor")
    print("=" * 50)
    
    # Get configuration from environment
    base_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    target_model = os.getenv('OLLAMA_MODEL', 'mistral')
    
    monitor = OllamaProgressMonitor(base_url)
    
    # Run health check first
    if not monitor.run_health_check():
        print("❌ Health check failed. Please ensure Ollama is running.")
        return
    
    print("\n" + "=" * 50)
    
    # Check if target model exists
    if not monitor.get_model_info(target_model):
        print(f"📥 Target model {target_model} not found. Starting download...")
        success = monitor.monitor_pull_progress(target_model)
        
        if success:
            print(f"🎉 {target_model} model is now ready!")
        else:
            print(f"💥 Failed to download {target_model} model")
            return
    else:
        print(f"✅ Target model {target_model} is already available")
    
    print("\n🎯 Ollama is ready for use!")

if __name__ == "__main__":
    main()
