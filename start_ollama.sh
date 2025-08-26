#!/bin/bash
# Startup script for Ki AI Model with Ollama

echo "🚀 Starting Ki AI Model with Ollama..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed. Installing now..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

# Check if port 11434 is already in use
if lsof -i :11434 > /dev/null 2>&1; then
    echo "⚠️  Port 11434 is already in use. Checking if it's our Ollama instance..."
    
    # Check if it's our Ollama process
    if pgrep -f "ollama serve" > /dev/null; then
        echo "✅ Found existing Ollama process, will use it"
        OLLAMA_PID=$(pgrep -f "ollama serve")
        echo "🤖 Using existing Ollama with PID: $OLLAMA_PID"
    else
        echo "❌ Port 11434 is in use by another process. Stopping it..."
        lsof -ti :11434 | xargs kill -9
        sleep 2
    fi
fi

# Start Ollama service in background (if not already running)
if [ -z "$OLLAMA_PID" ]; then
    echo "🤖 Starting Ollama service..."
    # Use 0.0.0.0 instead of default 127.0.0.1 for Render compatibility
    OLLAMA_HOST=0.0.0.0 ollama serve &
    OLLAMA_PID=$!
    echo "🤖 Ollama started with PID: $OLLAMA_PID"
fi

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to be ready..."
sleep 15

# Check if Ollama is responding
echo "🔍 Checking Ollama status..."
max_attempts=10
attempt=0
while [ $attempt -lt $max_attempts ]; do
    if curl -f http://localhost:11434/api/tags &> /dev/null; then
        echo "✅ Ollama is running and responding"
        break
    else
        attempt=$((attempt + 1))
        echo "⏳ Attempt $attempt/$max_attempts: Ollama not responding yet, waiting..."
        sleep 10
    fi
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ Ollama failed to start after $max_attempts attempts"
    echo "🔍 Checking Ollama process status..."
    if [ -n "$OLLAMA_PID" ]; then
        if ps -p $OLLAMA_PID > /dev/null; then
            echo "📊 Ollama process is running (PID: $OLLAMA_PID)"
            echo "📋 Process details:"
            ps -p $OLLAMA_PID -o pid,ppid,cmd
        else
            echo "❌ Ollama process is not running"
        fi
    fi
    echo "🔍 Checking port usage:"
    lsof -i :11434 || echo "Port 11434 is free"
    exit 1
fi

# Check if the required model is available
echo "📋 Checking available models..."
if ollama list | grep -q "mistral"; then
    echo "✅ Mistral model is already available"
else
    echo "📥 Mistral model not found. Starting download..."
    
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
echo "📱 Using main application: app.py"

# Start the main application
# Note: This will replace the current shell process with gunicorn
exec gunicorn --bind 0.0.0.0:5001 --workers 2 --timeout 120 app:app
