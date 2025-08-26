#!/bin/bash
# Debug script to identify what's running on the port and fix conflicts

echo "🔍 Debugging startup issues..."

# Check what's running on the port
PORT=${PORT:-5001}
echo "📍 Checking port $PORT..."

# Check if anything is listening on the port
if lsof -i :$PORT > /dev/null 2>&1; then
    echo "⚠️ Port $PORT is in use by:"
    lsof -i :$PORT
    echo ""
    
    # Check if it's our Flask app
    if pgrep -f "gunicorn.*app:app" > /dev/null; then
        echo "✅ Found gunicorn Flask app running"
    else
        echo "❌ No gunicorn Flask app found"
    fi
    
    # Check if it's Ollama
    if pgrep -f "ollama serve" > /dev/null; then
        echo "✅ Found Ollama running"
    else
        echo "❌ No Ollama found"
    fi
    
    # Check for other processes
    echo "🔍 Other processes that might be using the port:"
    ps aux | grep -E "(gunicorn|ollama|python|flask|gin)" | grep -v grep || echo "No relevant processes found"
else
    echo "✅ Port $PORT is free"
fi

echo ""
echo "🔍 Environment variables:"
echo "  PORT: $PORT"
echo "  FLASK_APP: ${FLASK_APP:-not set}"
echo "  FLASK_ENV: ${FLASK_ENV:-not set}"
echo "  PYTHONPATH: ${PYTHONPATH:-not set}"

echo ""
echo "🔍 Testing Flask app directly..."
python3 -c "
import os
import sys
sys.path.insert(0, os.getcwd())
try:
    from app import app
    print('✅ Flask app imports successfully')
    print(f'📱 App name: {app.name}')
    print(f'🔧 Debug mode: {app.debug}')
except Exception as e:
    print(f'❌ Flask app import failed: {e}')
"

echo ""
echo "🔍 Testing gunicorn..."
if command -v gunicorn > /dev/null; then
    echo "✅ gunicorn is available"
    gunicorn --version
else
    echo "❌ gunicorn not found"
fi

echo ""
echo "🔧 Attempting to fix port conflicts..."

# Kill any conflicting processes
echo "🔄 Killing conflicting processes..."
pkill -f "gin" 2>/dev/null || echo "No gin processes found"
pkill -f "gunicorn" 2>/dev/null || echo "No gunicorn processes found"
pkill -f "ollama serve" 2>/dev/null || echo "No ollama serve processes found"

# Wait a moment
sleep 3

# Check if port is now free
if lsof -i :$PORT > /dev/null 2>&1; then
    echo "⚠️ Port $PORT is still in use after killing processes"
    echo "🔄 Force killing processes on port $PORT..."
    lsof -ti :$PORT | xargs kill -KILL 2>/dev/null || echo "No processes to kill"
    sleep 2
else
    echo "✅ Port $PORT is now free"
fi

echo ""
echo "🚀 Starting Flask app directly for testing..."
echo "📱 This will start the Flask app on port $PORT"
echo "🔧 Press Ctrl+C to stop the test"

# Start Flask app directly for testing
python3 app.py
