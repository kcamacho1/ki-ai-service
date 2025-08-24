# Training Data Management

## Overview

This repository contains AI training data for the Ki Wellness AI Service. Large files (PDFs, images) are excluded from git due to size limitations, but essential training data (markdown, JSON, CSV) is included.

## File Structure

```
training_files/
├── 📁 Essential Data (included in git)
│   ├── *.md          # Markdown training guides
│   ├── *.json        # JSON training data
│   ├── *.csv         # CSV reference tables
│   └── *.txt         # Text training files
│
├── 🚫 Large Files (excluded from git)
│   ├── *.pdf         # PDF training materials
│   ├── *.jpg/*.jpeg  # Training images
│   ├── *.png         # Training graphics
│   └── original_large_pdfs/  # Source PDFs
│
└── 📋 Training Categories
    ├── Nutrition guides
    ├── Exercise materials
    ├── Health assessments
    └── Wellness resources
```

## What's Included in Git

### ✅ **Essential Training Data**
- `coaching_flow.md` - Coaching workflow guide
- `workout_plan.md` - Exercise plan templates
- `meal_plan.md` - Meal planning guides
- `red_flags.md` - Health warning signs
- `glossary.csv` - Health terminology
- `nutrient_reference_data.json` - Nutrition data
- `supplement_safety.json` - Supplement information
- `complete_nutrient_reference_table.csv` - Nutrient database

### 🚫 **Excluded Large Files**
- PDF training materials (too large for git)
- Training images and graphics
- Original large PDF documents
- Split PDF parts

## Getting Training Data

### **Option 1: Download from Source**
If you have access to the original training materials:
1. Download the large PDFs and images
2. Place them in the `training_files/` directory
3. The AI service will automatically detect and use them

### **Option 2: Use Existing Data**
The essential training data included in git provides a solid foundation:
- Nutrition and wellness guides
- Exercise and meal planning
- Health assessment tools
- Reference databases

### **Option 3: Generate New Training Data**
Use the AI service's training endpoints to create new examples:
```bash
# Create training examples
curl -X POST http://localhost:5001/api/training/create-example \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How can I boost my energy naturally?",
    "answer": "Focus on whole foods, regular exercise, and adequate sleep...",
    "category": "nutrition"
  }'
```

## Training Data Sources

### **Nutrition & Wellness**
- Dietary guidelines and recommendations
- Meal planning strategies
- Nutrient reference data
- Supplement safety information

### **Exercise & Fitness**
- Workout plans and routines
- Exercise safety guidelines
- Fitness assessment tools
- Movement correction exercises

### **Health Assessment**
- Screening forms and questionnaires
- Medical history templates
- Health risk assessments
- Wellness evaluation tools

## Using Training Data

### **1. Start the AI Service**
```bash
./start.sh
```

### **2. Process Training Files**
```bash
curl -X POST http://localhost:5001/api/training/process-files \
  -H "X-API-Key: your-key"
```

### **3. Check Training Status**
```bash
curl http://localhost:5001/api/training/status \
  -H "X-API-Key: your-key"
```

### **4. Search Knowledge Base**
```bash
curl -X POST http://localhost:5001/api/training/knowledge-base/search \
  -H "X-API-Key: your-key" \
  -H "Content-Type: application/json" \
  -d '{"query": "nutrition", "limit": 5}'
```

## Adding New Training Data

### **Small Files (< 100MB)**
1. Add to `training_files/` directory
2. Commit to git
3. The AI service will automatically process them

### **Large Files (> 100MB)**
1. Add to `training_files/` directory
2. Update `.gitignore` if needed
3. Document the file in this README
4. Provide download instructions

### **Training Examples**
Use the API to create structured training examples:
```python
from apis.ai_service_client import AIServiceClient

client = AIServiceClient()
client.create_training_example(
    question="What are the benefits of meditation?",
    answer="Meditation reduces stress, improves focus...",
    category="wellness"
)
```

## Best Practices

### **Data Quality**
- Use accurate, evidence-based information
- Include proper citations and sources
- Maintain consistent formatting
- Regular updates and validation

### **File Organization**
- Group related materials together
- Use descriptive filenames
- Maintain version control for essential data
- Document data sources and updates

### **Performance**
- Keep essential data in git for quick access
- Use large files locally for training
- Implement caching for frequently accessed data
- Monitor training data size and impact

## Troubleshooting

### **Missing Training Files**
If the AI service can't find expected training data:
1. Check if files are in the correct directory
2. Verify file permissions
3. Check the training status endpoint
4. Review the service logs

### **Large File Issues**
If you encounter issues with large files:
1. Ensure they're properly excluded from git
2. Check available disk space
3. Verify the AI service can access the files
4. Consider splitting very large files

## Support

For questions about training data:
1. Check the AI service logs
2. Review the training endpoints
3. Verify file permissions and paths
4. Contact the development team

---

**Note**: This repository focuses on code and essential training data. Large training materials should be obtained separately and placed in the `training_files/` directory for local use.
