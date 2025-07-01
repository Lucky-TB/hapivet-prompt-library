# 🚀 Hapivet Prompt Library

> **Intelligent AI Model Routing & Cost Optimization**

A Python-based prompt library that automatically routes requests to the best AI models, optimizes costs, and monitors usage in real-time.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)

---

## ✨ Features

- 🤖 **Multi-Model Support**: OpenAI, Anthropic, Google Gemini, DeepSeek
- 💰 **Smart Cost Optimization**: Free tier management, model rotation
- 📊 **Usage Monitoring**: Token tracking, spike detection, alerts
- 🛡️ **Fraud Detection**: Pattern detection, risk scoring
- 🎯 **Auto-Selection**: Picks best model based on prompt type and cost

---

## 🚀 Quick Start

### 1. **Setup**
```bash
git clone <your-repo-url>
cd hapivet-prompt-library
pip install -r requirements.txt
cp env.example .env
```

### 2. **Configure API Keys**
Edit `.env`:
```env
GOOGLE_API_KEY=your_google_key
DEEPSEEK_API_KEY=your_deepseek_key
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
```

### 3. **Run**
```bash
python run.py
```

### 4. **Access**
- 🌐 **API Docs**: http://localhost:8000/docs
- 🎮 **Examples**: http://localhost:8000/examples
- 🏥 **Health**: http://localhost:8000/api/v1/health

---

## 📚 API Usage

### Submit Prompt
```bash
curl -X POST "http://localhost:8000/api/v1/demo/prompt" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a Python function for fibonacci",
    "model_preference": "auto"
  }'
```

### Get Models
```bash
curl "http://localhost:8000/api/v1/models"
```

### Cost Analysis
```bash
curl "http://localhost:8000/api/v1/demo/cost-analysis"
```

---

## 🏗️ Architecture

```
src/
├── models/          # AI model adapters
├── services/        # Core business logic
├── utils/           # Utilities
└── api/             # FastAPI app
```

### Key Services
- **Model Manager**: Routes to best AI models
- **Usage Monitor**: Tracks usage & detects anomalies  
- **Cost Optimizer**: Manages costs & free tiers
- **Fraud Detector**: Detects suspicious patterns

---

## 🆓 Free Models

| Provider | Model | Free Tier |
|----------|-------|-----------|
| **Google** | Gemini 1.5 Flash | 2,500 req/day, 50M tokens/month |
| **Google** | Gemini 1.5 Pro | 1,500 req/day, 15M tokens/month |
| **DeepSeek** | DeepSeek Chat | Limited free, then $0.0014/1K tokens |
| **OpenAI** | GPT-3.5-turbo | $5 free credit for new users |

---

## 🧪 Testing

```bash
# Test API keys
python test_api_keys.py

# Run tests
pytest tests/
```

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
