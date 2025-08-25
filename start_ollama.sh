#!/bin/bash
# Startup script for Ki AI Model with Ollama

echo "🚀 Starting Ki AI Model with Ollama..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed. Installing now..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

# Start Ollama service in background
echo "🤖 Starting Ollama service..."
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to be ready..."
sleep 15

# Check if Ollama is responding
echo "🔍 Checking Ollama status..."
if curl -f http://localhost:11434/api/tags &> /dev/null; then
    echo "✅ Ollama is running and responding"
else
    echo "❌ Ollama is not responding, waiting longer..."
    sleep 10
fi

# Check if the required model is available
echo "📋 Checking available models..."
if ollama list | grep -q "mistral"; then
    echo "✅ Mistral model is already available"
else
    echo "📥 Mistral model not found. Starting download with progress monitoring..."
    
    # Use Python progress monitor if available
    if command -v python3 &> /dev/null && [ -f "ollama_progress.py" ]; then
        echo "🐍 Using Python progress monitor for detailed download tracking..."
        python3 ollama_progress.py
    else
        echo "📥 Using basic progress monitoring..."
        echo "⏳ This may take several minutes depending on your internet connection..."
        
        # Start the pull with basic progress monitoring
        ollama pull mistral 2>&1 | while IFS= read -r line; do
            if [[ $line == *"downloading"* ]]; then
                echo "📥 Downloading model layers..."
            elif [[ $line == *"verifying"* ]]; then
                echo "🔍 Verifying model integrity..."
            elif [[ $line == *"writing"* ]]; then
                echo "💾 Writing model to disk..."
            elif [[ $line == *"success"* ]]; then
                echo "✅ Model download completed successfully!"
            elif [[ $line == *"error"* ]]; then
                echo "❌ Error during download: $line"
            else
                echo "📊 $line"
            fi
        done
    fi
    
    # Check if pull was successful
    if ollama list | grep -q "mistral"; then
        echo "✅ Mistral model is now available"
    else
        echo "❌ Failed to download Mistral model"
        exit 1
    fi
fi

echo "🎯 Starting Ki AI Model application..."
echo "🤖 Ollama is running with PID: $OLLAMA_PID"

# Start the main application
exec gunicorn --bind 0.0.0.0:5001 --workers 2 --timeout 120 simple_app:app
