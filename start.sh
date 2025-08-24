#!/bin/bash

# Ki Wellness AI Service Startup Script

echo "🚀 Starting Ki Wellness AI Service..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Please copy env.example to .env and configure it."
    echo "   cp env.example .env"
    echo "   Then edit .env with your configuration."
    exit 1
fi

# Check if database is accessible
echo "🗄️  Checking database connection..."
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
import psycopg2
try:
    conn = psycopg2.connect(os.getenv('AI_SERVICE_DATABASE_URL'))
    conn.close()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

if [ $? -ne 0 ]; then
    echo "❌ Database connection failed. Please check your configuration."
    exit 1
fi

# Start the service
echo "🌟 Starting AI service on port 5001..."
python app.py
