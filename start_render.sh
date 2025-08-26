#!/bin/bash
# Render-optimized startup script for Ki AI Model with Ollama

echo "🚀 Starting Ki AI Model on Render..."

# Set Render-specific environment variables
# Use Render's PORT environment variable (required for Render deployment)
export PORT=${PORT:-5001}
export OLLAMA_HOST=${OLLAMA_HOST:-localhost}
export OLLAMA_PORT=${OLLAMA_PORT:-11434}

echo "🔧 Environment Configuration:"
echo "  PORT: $PORT (Render's port binding)"
echo "  OLLAMA_HOST: $OLLAMA_HOST"
echo "  OLLAMA_PORT: $OLLAMA_PORT"
echo "  OLLAMA_MODEL: ${OLLAMA_MODEL:-mistral}"

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed. Installing now..."
    curl -fsSL https://ollama.ai/install.sh | sh
fi

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -i :$port > /dev/null 2>&1; then
        echo "⚠️  Port $port is already in use"
        lsof -i :$port
        return 0
    else
        echo "✅ Port $port is free"
        return 1
    fi
}

# Check and handle port conflicts
if check_port 11434; then
    echo "🔍 Checking what's using port 11434..."
    
    # Check if it's our Ollama process
    if pgrep -f "ollama serve" > /dev/null; then
        echo "✅ Found existing Ollama process, will use it"
        OLLAMA_PID=$(pgrep -f "ollama serve")
        echo "🤖 Using existing Ollama with PID: $OLLAMA_PID"
    else
        echo "❌ Port 11434 is in use by another process. Attempting to free it..."
        # Try to gracefully stop the process
        lsof -ti :11434 | xargs kill -TERM 2>/dev/null || true
        sleep 3
        
        # Force kill if still in use
        if check_port 11434; then
            echo "🔄 Force killing process on port 11434..."
            lsof -ti :11434 | xargs kill -KILL 2>/dev/null || true
            sleep 2
        fi
    fi
fi

# Start Ollama service in background (if not already running)
if [ -z "$OLLAMA_PID" ]; then
    echo "🤖 Starting Ollama service..."
    echo "📍 Binding to: $OLLAMA_HOST:11434"
    
    # Start Ollama with explicit host binding
    OLLAMA_HOST=0.0.0.0 ollama serve &
    OLLAMA_PID=$!
    echo "🤖 Ollama started with PID: $OLLAMA_PID"
    
    # Wait for Ollama to be ready
    echo "⏳ Waiting for Ollama to be ready..."
    sleep 20  # Increased wait time for Render
    
    # Check if Ollama is responding
    echo "🔍 Checking Ollama status..."
    max_attempts=15  # Increased attempts for Render
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
        echo "🔍 Debugging information:"
        echo "  Ollama PID: $OLLAMA_PID"
        echo "  Process status:"
        ps aux | grep ollama || echo "No ollama processes found"
        echo "  Port usage:"
        lsof -i :11434 || echo "Port 11434 is free"
        echo "  Ollama logs:"
        echo "  Attempting to continue anyway..."
    fi
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
        echo "🔄 Attempting to continue anyway..."
    fi
fi

echo "🎯 Starting Ki AI Model application..."
echo "🤖 Ollama is running with PID: $OLLAMA_PID"
echo "🌐 Binding to Render PORT: $PORT"
echo "📱 Using main application: app.py"

# Start the main application with Render port
# Use Render's PORT environment variable for proper port binding
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app
