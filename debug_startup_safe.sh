#!/bin/bash

echo "🔍 SAFE DEBUG SCRIPT - No process killing"
echo "=========================================="

# Check if we're in the right directory
echo "📁 Current directory: $(pwd)"
echo "📁 Expected files:"
ls -la app.py Dockerfile start_*.sh 2>/dev/null || echo "❌ Missing expected files"

# Check environment variables
echo ""
echo "🔧 Environment Variables:"
echo "DATABASE_URL: ${DATABASE_URL:+SET}"
echo "OLLAMA_HOST: ${OLLAMA_HOST:-NOT SET}"
echo "OLLAMA_PORT: ${OLLAMA_PORT:-NOT SET}"
echo "FLASK_ENV: ${FLASK_ENV:-NOT SET}"

# Check if port 5001 is in use (without killing anything)
echo ""
echo "🌐 Port 5001 status:"
if lsof -i :5001 >/dev/null 2>&1; then
    echo "⚠️  Port 5001 is in use by:"
    lsof -i :5001
else
    echo "✅ Port 5001 is available"
fi

# Check if port 11434 is in use (Ollama)
echo ""
echo "🤖 Port 11434 status (Ollama):"
if lsof -i :11434 >/dev/null 2>&1; then
    echo "⚠️  Port 11434 is in use by:"
    lsof -i :11434
else
    echo "✅ Port 11434 is available"
fi

# Test Flask app import
echo ""
echo "🐍 Testing Flask app import:"
python3 -c "
try:
    from app import app
    print('✅ Flask app imports successfully')
    print(f'App name: {app.name}')
    print(f'App config: {dict(app.config)}')
except Exception as e:
    print(f'❌ Flask app import failed: {e}')
"

# Check gunicorn availability
echo ""
echo "🚀 Gunicorn availability:"
if command -v gunicorn >/dev/null 2>&1; then
    echo "✅ Gunicorn is available"
    gunicorn --version
else
    echo "❌ Gunicorn not found"
fi

# Check if we can start the app manually
echo ""
echo "🧪 Testing manual app start (will timeout after 5 seconds):"
timeout 5s python3 -c "
from app import app
app.run(host='0.0.0.0', port=5001, debug=False)
" 2>&1 | head -10 || echo "App start test completed"

echo ""
echo "✅ Safe debug complete - no processes were killed"
