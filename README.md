# Ki Wellness AI Service

A standalone AI service that provides AI chat, analysis, and training capabilities for the Ki Wellness application.

## Overview

This service extracts all AI-related functionality from the main Ki Wellness app into a dedicated, scalable service that can be deployed independently. It includes:

- **AI Chat**: Intelligent health coaching conversations
- **AI Analysis**: Personalized wellness pattern analysis
- **Training System**: Model fine-tuning and knowledge base management
- **Health Resources**: Curated health information and links
- **API Management**: Secure, rate-limited API endpoints

## Architecture

```
ki_ai_service/
├── api/                    # API blueprints
│   ├── chat.py           # Chat endpoints
│   ├── analysis.py       # Analysis endpoints
│   ├── training.py       # Training endpoints
│   └── health.py         # Health monitoring
├── models/                # Database models
│   └── database.py       # Database connection and models
├── resources/             # Static resources
│   └── health_resources.py # Health information database
├── utils/                 # Utility functions
│   └── auth.py           # Authentication and security
├── training_files/        # Training data files
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Local development setup
└── README.md             # This file
```

## Features

### 🤖 AI Chat
- Context-aware health coaching
- Fallback responses when AI is unavailable
- Session management and user tracking
- Resource linking to Medium blog and authoritative sources

### 📊 AI Analysis
- Personalized wellness pattern analysis
- Data-driven insights from user logs
- Actionable health suggestions
- Pattern recognition across food, water, and mood data

### 🎯 Training System
- Model fine-tuning capabilities
- Knowledge base management
- Training example collection
- Performance feedback tracking

### 🔒 Security
- API key authentication
- Rate limiting
- Input sanitization
- CORS configuration

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL database
- Ollama (for local AI models)
- Docker (optional)

### Local Development

1. **Clone and setup**
   ```bash
   cd ki_ai_service
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Environment configuration**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

3. **Database setup**
   ```bash
   # Create PostgreSQL database
   createdb ki_ai_service_db
   
   # The app will create tables automatically on first run
   ```

4. **Start Ollama**
   ```bash
   # Install Ollama from https://ollama.ai
   ollama pull mistral
   ollama serve
   ```

5. **Run the service**
   ```bash
   python app.py
   ```

### Docker Development

1. **Start services**
   ```bash
   docker-compose up -d
   ```

2. **Check status**
   ```bash
   curl http://localhost:5001/api/health/check
   ```

## API Endpoints

### Authentication
All endpoints require an API key in the `X-API-Key` header or `api_key` query parameter.

### Chat API
- `POST /api/chat/message` - Send chat message
- `POST /api/chat/enhanced` - Enhanced chat with fine-tuned model

### Analysis API
- `POST /api/analysis/generate` - Generate AI analysis
- `POST /api/analysis/user-summary` - Get user data summary

### Training API
- `GET /api/training/status` - Training system status
- `POST /api/training/process-files` - Process training files
- `POST /api/training/create-example` - Create training example
- `POST /api/training/fine-tune` - Fine-tune model
- `POST /api/training/knowledge-base/search` - Search knowledge base

### Health API
- `GET /api/health/check` - Basic health check
- `GET /api/health/detailed` - Detailed health status
- `GET /api/health/ready` - Readiness check
- `GET /api/health/live` - Liveness check

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AI_SERVICE_DATABASE_URL` | PostgreSQL connection string | Required |
| `AI_SERVICE_SECRET_KEY` | Flask secret key | Required |
| `VALID_API_KEYS` | Comma-separated API keys | Required |
| `OLLAMA_MODEL` | Base AI model name | `mistral` |
| `FINE_TUNED_MODEL` | Fine-tuned model name | `ki-wellness-mistral` |
| `AI_SERVICE_PORT` | Service port | `5001` |
| `AI_SERVICE_DEBUG` | Debug mode | `false` |
| `ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:5000` |

### Database Schema

The service creates the following tables:
- `knowledge_base` - Processed training content
- `training_examples` - Training data for fine-tuning
- `model_performance` - Model performance tracking
- `user_interactions` - User interaction logs
- `api_usage` - API usage tracking

## Integration with Ki Wellness App

The main Ki Wellness app can communicate with this service using the provided API client:

```python
from apis.ai_service_client import AIServiceClient

# Initialize client
client = AIServiceClient(
    base_url='http://your-ai-service:5001',
    api_key='your-api-key'
)

# Send chat message
response = client.chat_message(
    message="How can I boost my energy?",
    user_id="user123",
    context={'context_type': 'nutrition'}
)

if response.get('success'):
    ai_response = response.get('response')
else:
    # Handle error or use fallback
    fallback = client.get_fallback_response("How can I boost my energy?", "nutrition")
```

## Deployment

### Production Considerations

1. **Database**: Use managed PostgreSQL service
2. **AI Models**: Consider cloud-based Ollama or other AI services
3. **Scaling**: Use load balancer and multiple instances
4. **Monitoring**: Implement proper logging and metrics
5. **Security**: Use HTTPS, rotate API keys regularly

### Docker Production

```bash
# Build and run
docker build -t ki-ai-service .
docker run -d -p 5001:5001 --env-file .env ki-ai-service
```

### Kubernetes

The service includes health check endpoints (`/ready`, `/live`) for Kubernetes deployment.

## Development

### Adding New Endpoints

1. Create new blueprint in `api/` directory
2. Register in `app.py`
3. Add authentication decorators
4. Update documentation

### Testing

```bash
# Run tests (when implemented)
python -m pytest tests/

# Manual testing
curl -H "X-API-Key: your-key" http://localhost:5001/api/health/check
```

### Logging

The service logs to stdout/stderr. In production, configure proper logging to files or centralized logging service.

## Troubleshooting

### Common Issues

1. **Ollama Connection Failed**
   - Ensure Ollama is running: `ollama serve`
   - Check model is downloaded: `ollama list`

2. **Database Connection Failed**
   - Verify database is running and accessible
   - Check connection string in environment variables

3. **API Key Rejected**
   - Verify API key is correct
   - Check `VALID_API_KEYS` environment variable

### Health Checks

Use the health endpoints to diagnose issues:
- `/api/health/check` - Basic status
- `/api/health/detailed` - Component-level status
- `/api/health/ready` - Service readiness

## Contributing

1. Follow the existing code structure
2. Add proper error handling
3. Include API documentation
4. Test thoroughly
5. Update this README

## License

This service is part of the Ki Wellness project and follows the same licensing terms.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the health endpoints
3. Check application logs
4. Contact the development team
