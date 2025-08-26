FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads

# Make startup scripts executable
RUN chmod +x start_ollama.sh start_render.sh start_simple.sh start_production.sh debug_startup.sh

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_MODEL=mistral
ENV OLLAMA_HOST=localhost
ENV OLLAMA_PORT=11434

# Note: Don't expose a hardcoded port - let Render handle port binding
# Render will provide the PORT environment variable at runtime

# Health check - use the Flask app's health endpoint
# Use $PORT environment variable for health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-5001}/health || exit 1

# Use the production startup script
CMD ["./start_production.sh"]
