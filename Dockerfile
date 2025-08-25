FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies including Ollama
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
RUN chmod +x start_ollama.sh

# Pull the required Ollama model
RUN ollama pull mistral

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=simple_app.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV OLLAMA_MODEL=mistral
ENV OLLAMA_BASE_URL=http://localhost:11434

# Expose port
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/api/status || exit 1

# Use the startup script
CMD ["./start_ollama.sh"]
