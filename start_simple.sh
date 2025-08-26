#!/bin/bash
# Simplified startup script for Ki AI Model - focuses on Flask app

echo "🚀 Starting Ki AI Model (Simplified)..."

# Set environment variables
# Use Render's PORT environment variable (required for Render deployment)
export PORT=${PORT:-5001}
export FLASK_APP=app.py
export FLASK_ENV=production
export PYTHONUNBUFFERED=1

echo "🔧 Environment Configuration:"
echo "  PORT: $PORT (Render's port binding)"
echo "  FLASK_APP: $FLASK_APP"
echo "  FLASK_ENV: $FLASK_ENV"

# Check if port is in use
if lsof -i :$PORT > /dev/null 2>&1; then
    echo "⚠️ Port $PORT is in use. Killing existing processes..."
    lsof -ti :$PORT | xargs kill -KILL 2>/dev/null || true
    sleep 2
fi

# Test Flask app import
echo "🔍 Testing Flask app..."
python3 -c "
import os
import sys
sys.path.insert(0, os.getcwd())
try:
    from app import app
    print('✅ Flask app imports successfully')
except Exception as e:
    print(f'❌ Flask app import failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Flask app test failed. Exiting."
    exit 1
fi

echo "🎯 Starting Flask application..."
echo "🌐 Binding to Render PORT: $PORT"
echo "📱 Using main application: app.py"

# Start the Flask app with gunicorn
# Use Render's PORT environment variable for proper port binding
exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --timeout 120 --preload app:app
