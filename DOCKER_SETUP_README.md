# Docker Setup for Ki AI Model

## 🚨 Problem Solved

The original Docker build was failing because:
```dockerfile
RUN ollama pull mistral  # ❌ This fails during build time
```

**Why it failed:** The `ollama pull` command expects the Ollama server to be running, but during `docker build`, no services are running yet.

## ✅ Solutions

### **Option 1: All-in-One Container (Simple)**

**Use this if you want:** Quick setup, single container, development/testing

**Files to use:**
- `Dockerfile` (updated)
- `docker-compose.yml` (existing)

**How it works:**
1. Container starts
2. `ollama serve` runs in background
3. Waits 10 seconds for server to be ready
4. `ollama pull mistral` downloads the model
5. Your app starts

**Pros:**
- ✅ Simple setup
- ✅ Single container
- ✅ Works immediately

**Cons:**
- ❌ Larger container size
- ❌ Model downloads every time container restarts
- ❌ Less production-ready

---

### **Option 2: Separate Containers (Production)**

**Use this if you want:** Production setup, persistent models, better separation of concerns

**Files to use:**
- `Dockerfile.production`
- `docker-compose.production.yml`
- `setup_production.sh`

**How it works:**
1. **Ollama container** runs separately with persistent volume
2. **App container** connects to Ollama via network
3. **Models persist** between container restarts
4. **Better resource management**

**Pros:**
- ✅ Production-ready
- ✅ Models persist in volumes
- ✅ Better resource isolation
- ✅ Easier scaling
- ✅ Cleaner architecture

**Cons:**
- ❌ More complex setup
- ❌ Multiple containers to manage

---

## 🚀 Quick Start

### **Option 1: All-in-One (Recommended for Development)**

```bash
# Build and run
docker-compose up --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f ki-ai-service
```

### **Option 2: Production Setup**

```bash
# Run the setup script
./setup_production.sh

# Or manually:
docker-compose -f docker-compose.production.yml up --build -d

# Pull the model (one-time setup)
docker-compose -f docker-compose.production.yml exec ollama ollama pull mistral
```

---

## 📁 File Structure

```
ki_ai_model/
├── Dockerfile                    # Option 1: All-in-one
├── Dockerfile.production         # Option 2: App only
├── docker-compose.yml            # Option 1: All-in-one
├── docker-compose.production.yml # Option 2: Separate containers
├── setup_production.sh           # Option 2: Setup script
├── start_ollama.sh              # Startup script (Option 1)
└── templates/
    ├── index.html               # Main dashboard
    └── api_keys.html            # API keys management
```

---

## 🔧 Configuration

### **Environment Variables**

**Option 1 (All-in-one):**
```bash
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
```

**Option 2 (Production):**
```bash
OLLAMA_BASE_URL=http://ollama:11434  # Note: 'ollama' is container name
OLLAMA_MODEL=mistral
```

### **Ports**

- **Ki AI Service**: `5001`
- **Ollama**: `11434`
- **Database**: `5433`

---

## 🐛 Troubleshooting

### **Common Issues**

**1. "Ollama server not responding"**
- **Solution**: Wait longer for Ollama to start (increased sleep time)
- **Check**: `docker-compose logs ollama`

**2. "Model not found"**
- **Solution**: Model download failed during startup
- **Check**: `docker-compose logs ki-ai-service`

**3. "Connection refused"**
- **Solution**: Check if all services are running
- **Check**: `docker-compose ps`

### **Debug Commands**

```bash
# Check container status
docker-compose ps

# View logs for specific service
docker-compose logs -f ki-ai-service
docker-compose logs -f ollama

# Exec into container
docker-compose exec ki-ai-service bash
docker-compose exec ollama bash

# Check Ollama status
curl http://localhost:11434/api/tags
```

---

## 📊 Performance Comparison

| Aspect | Option 1 (All-in-one) | Option 2 (Production) |
|--------|------------------------|------------------------|
| **Startup Time** | Slower (downloads model) | Faster (model cached) |
| **Memory Usage** | Higher (single container) | Lower (distributed) |
| **Model Persistence** | ❌ Lost on restart | ✅ Persistent |
| **Scalability** | ❌ Limited | ✅ Better |
| **Production Ready** | ❌ No | ✅ Yes |

---

## 🎯 Recommendations

### **For Development/Testing:**
- Use **Option 1** (all-in-one)
- Simple setup, works immediately
- Good for local development

### **For Production:**
- Use **Option 2** (separate containers)
- Better performance and reliability
- Models persist between deployments
- Easier to scale and maintain

---

## 🔄 Migration

### **From Option 1 to Option 2:**

1. **Stop current services:**
   ```bash
   docker-compose down
   ```

2. **Use production setup:**
   ```bash
   ./setup_production.sh
   ```

3. **Verify migration:**
   ```bash
   curl http://localhost:5001/api/status
   ```

---

## 📚 Additional Resources

- [Ollama Documentation](https://ollama.ai/docs)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Ki AI Model API Documentation](API_KEYS_PAGE_README.md)

---

## 🆘 Need Help?

If you encounter issues:

1. **Check the logs**: `docker-compose logs -f`
2. **Verify container status**: `docker-compose ps`
3. **Check network connectivity**: `docker network ls`
4. **Restart services**: `docker-compose restart`
