#!/bin/bash
# Production startup script for Ki AI Model - ensures Flask app starts properly

echo "🚀 Starting Ki AI Model in Production Mode..."

# Set production environment variables
# Use Render's PORT environment variable (required for Render deployment)
export PORT=${PORT:-5001}
export FLASK_APP=app.py
export FLASK_ENV=production
export PYTHONUNBUFFERED=1
export OLLAMA_HOST=${OLLAMA_HOST:-localhost}
export OLLAMA_PORT=${OLLAMA_PORT:-11434}

echo "🔧 Production Environment Configuration:"
echo "  PORT: $PORT (Render's port binding)"
echo "  FLASK_APP: $FLASK_APP"
echo "  FLASK_ENV: $FLASK_ENV"
echo "  OLLAMA_HOST: $OLLAMA_HOST"
echo "  OLLAMA_PORT: $OLLAMA_PORT"

# Kill any existing processes on our port
echo "🔍 Checking for existing processes on port $PORT..."
if lsof -i :$PORT > /dev/null 2>&1; then
    echo "⚠️ Port $PORT is in use. Stopping existing processes..."
    lsof -ti :$PORT | xargs kill -KILL 2>/dev/null || true
    sleep 3
fi

# Test Flask app import and basic functionality
echo "🔍 Testing Flask app..."
python3 -c "
import os
import sys
sys.path.insert(0, os.getcwd())
try:
    from app import app
    print('✅ Flask app imports successfully')
    
    # Test basic route
    with app.test_client() as client:
        response = client.get('/')
        if response.status_code == 200:
            print('✅ Root route responds correctly')
        else:
            print(f'⚠️ Root route returned status {response.status_code}')
            
except Exception as e:
    print(f'❌ Flask app test failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Flask app test failed. Exiting."
    exit 1
fi

# Start Ollama in background if needed
echo "🤖 Starting Ollama service..."
OLLAMA_HOST=0.0.0.0 ollama serve &
OLLAMA_PID=$!
echo "🤖 Ollama started with PID: $OLLAMA_PID"

# Wait for Ollama to be ready
echo "⏳ Waiting for Ollama to be ready..."
sleep 10

# Check if Ollama is responding
if curl -f http://localhost:11434/api/tags &> /dev/null; then
    echo "✅ Ollama is running and responding"
else
    echo "⚠️ Ollama may not be ready, but continuing..."
fi

echo "🎯 Starting Flask application with Gunicorn..."
echo "🌐 Binding to Render PORT: $PORT"
echo "📱 Using main application: app.py"

# Start the Flask app with gunicorn
# Use Render's PORT environment variable for proper port binding
exec gunicorn \
    --bind 0.0.0.0:$PORT \
    --workers 1 \
    --timeout 120 \
    --preload \
    --access-logfile - \
    --error-logfile - \
    app:app
