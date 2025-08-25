#!/bin/bash
# Production setup script for Ki AI Model with separate Ollama container

echo "🚀 Setting up Ki AI Model in Production Mode..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose > /dev/null && ! docker compose version > /dev/null 2>&1; then
    echo "❌ Docker Compose is not available. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker environment is ready"

# Create production docker-compose file if it doesn't exist
if [ ! -f "docker-compose.production.yml" ]; then
    echo "❌ Production docker-compose file not found. Please create docker-compose.production.yml first."
    exit 1
fi

# Build and start services
echo "🔨 Building and starting services..."
if command -v docker-compose > /dev/null; then
    docker-compose -f docker-compose.production.yml up --build -d
else
    docker compose -f docker-compose.production.yml up --build -d
fi

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service status
echo "🔍 Checking service status..."
if command -v docker-compose > /dev/null; then
    docker-compose -f docker-compose.production.yml ps
else
    docker compose -f docker-compose.production.yml ps
fi

# Pull the Mistral model in the Ollama container
echo "📥 Pulling Mistral model in Ollama container..."
if command -v docker-compose > /dev/null; then
    docker-compose -f docker-compose.production.yml exec ollama ollama pull mistral
else
    docker compose -f docker-compose.production.yml exec ollama ollama pull mistral
fi

echo ""
echo "🎉 Setup complete! Your services are now running:"
echo ""
echo "📱 Ki AI Service: http://localhost:5001"
echo "🤖 Ollama Service: http://localhost:11434"
echo "🗄️  Database: localhost:5433"
echo ""
echo "📊 To view logs:"
echo "   docker-compose -f docker-compose.production.yml logs -f"
echo ""
echo "🛑 To stop services:"
echo "   docker-compose -f docker-compose.production.yml down"
echo ""
echo "🔄 To restart services:"
echo "   docker-compose -f docker-compose.production.yml restart"
