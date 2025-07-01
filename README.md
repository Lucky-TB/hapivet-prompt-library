# 🚀 Hapivet Prompt Library

> **Intelligent AI Model Routing & Cost Optimization Platform**

A powerful Python-based prompt library that automatically routes requests to the best AI models, optimizes costs, monitors usage patterns, and detects fraud in real-time.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ✨ Features

### 🤖 **Multi-Model AI Support**
| Provider | Models | Specialties |
|----------|--------|-------------|
| **OpenAI** | GPT-4, GPT-3.5-turbo | Reasoning, Coding, Text Generation |
| **Anthropic** | Claude-3 | Long Context, Analysis |
| **Google** | Gemini Pro | Free Tier, General Purpose |
| **DeepSeek** | DeepSeek Chat, DeepSeek Coder | Cost-Effective, Code Generation |

### 💰 **Smart Cost Optimization**
- 🆓 **Free Tier Management**: Automatically uses free tiers first
- 🔄 **Model Rotation**: Switches models to stay within limits
- 📊 **Cost Tracking**: Real-time cost analysis and alerts
- 🎯 **Provider Ranking**: Sorts providers by cost efficiency

### 📈 **Usage Monitoring & Analytics**
- 📊 **Token Tracking**: Monitor usage per user and model
- ⚡ **Spike Detection**: Alerts for unusual usage patterns
- 📈 **Historical Analysis**: Track trends over time
- 🔔 **Real-time Alerts**: Instant notifications for anomalies

### 🛡️ **Fraud Detection & Security**
- 🚨 **Pattern Detection**: Identifies suspicious usage patterns
- 🌐 **IP Monitoring**: Tracks multiple IP addresses
- ⏰ **Time Analysis**: Detects unusual hour usage
- 🎯 **Risk Scoring**: Calculates user risk levels

### 🎯 **Intelligent Prompt Optimization**
- 🧠 **Auto-Detection**: Identifies prompt type (coding, reasoning, text)
- 🔧 **Model Adaptation**: Formats prompts for specific models
- 📝 **Template Generation**: Creates optimized prompt templates
- 💡 **Improvement Suggestions**: Recommends prompt enhancements

---

## 🚀 Quick Start

### 1️⃣ **Installation**

```bash
# Clone the repository
git clone <your-repo-url>
cd hapivet-prompt-library

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp env.example .env
```

### 2️⃣ **Configuration**

Edit your `.env` file with your API keys:

```env
# Database Configuration
DATABASE_URL=postgresql://user:password@localhost/hapivet
REDIS_URL=redis://localhost:6379

# AI Provider API Keys
OPENAI_API_KEY=your_openai_key_here
ANTHROPIC_API_KEY=your_anthropic_key_here
GOOGLE_API_KEY=your_google_key_here
DEEPSEEK_API_KEY=your_deepseek_key_here

# Monitoring & Security
SENTRY_DSN=your_sentry_dsn_here
SECRET_KEY=your_secret_key_here
ENVIRONMENT=development
```

### 3️⃣ **Database Setup**

```bash
# Create database tables
python -c "from src.utils.database import db_manager; db_manager.create_tables()"
```

### 4️⃣ **Launch Application**

```bash
# Option 1: Use the startup script
python run.py

# Option 2: Direct uvicorn command
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

### 5️⃣ **Access Your API**

| Service | URL | Description |
|---------|-----|-------------|
| 🌐 **API Documentation** | http://localhost:8000/docs | Interactive API docs |
| �� **Health Check** | http://localhost:8000/api/v1/health | System status |
| 📋 **Available Models** | http://localhost:8000/api/v1/models | List all AI models |

---

## 📚 API Usage Examples

### 🔤 **Submit a Prompt Request**

```bash
curl -X POST "http://localhost:8000/api/v1/prompt" \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a Python function to calculate fibonacci numbers",
    "context": "This is for a beginner programming tutorial",
    "max_tokens": 500
  }'
```

**Response:**
```json
{
  "id": "uuid-here",
  "response": "Here's a Python function to calculate fibonacci numbers...",
  "model_used": "google-gemini-pro",
  "tokens_used": 150,
  "cost": 0.0,
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### 📊 **Get Usage Statistics**

```bash
curl -X GET "http://localhost:8000/api/v1/usage/user123" \
  -H "Authorization: Bearer your-api-key"
```

### 💰 **Get Cost Analysis**

```bash
curl -X GET "http://localhost:8000/api/v1/cost-analysis" \
  -H "Authorization: Bearer your-api-key"
```

### 🚨 **Get Active Alerts**

```bash
curl -X GET "http://localhost:8000/api/v1/alerts" \
  -H "Authorization: Bearer your-api-key"
```

---

## 🏗️ Architecture Overview

### 🔧 **Core Services**

| Service | File | Purpose |
|---------|------|---------|
| **Model Manager** | `src/services/model_manager.py` | Routes requests to best AI models |
| **Usage Monitor** | `src/services/usage_monitor.py` | Tracks usage and detects anomalies |
| **Cost Optimizer** | `src/services/cost_optimizer.py` | Manages costs and free tier limits |
| **Fraud Detector** | `src/services/fraud_detector.py` | Detects suspicious patterns |
| **Prompt Optimizer** | `src/services/prompt_optimizer.py` | Optimizes prompts for models |

### 🤖 **AI Model Adapters**

| Adapter | File | Provider |
|---------|------|----------|
| **OpenAI** | `src/models/openai_model.py` | GPT-4, GPT-3.5-turbo |
| **Anthropic** | `src/models/anthropic_model.py` | Claude-3 |
| **Google** | `src/models/gemini_model.py` | Gemini Pro |
| **DeepSeek** | `src/models/deepseek_model.py` | DeepSeek Chat/Coder |

### 📁 **Project Structure**

```
hapivet-prompt-library/
├── 📁 src/
│   ├── 📁 models/          # AI model adapters
│   ├── 📁 services/        # Core business logic
│   ├── 📁 utils/           # Utilities and helpers
│   └── 📁 api/             # FastAPI application
├── 📁 tests/               # Test files
├── 📄 requirements.txt     # Python dependencies
├── 📄 config.yaml         # Model configurations
├── 📄 env.example         # Environment template
├── 📄 run.py              # Startup script
└── 📄 README.md           # This file
```

---

## ⚙️ Configuration

### 🎛️ **Model Configuration** (`config.yaml`)

```yaml
models:
  openai:
    gpt-4:
      cost_per_1k_tokens: 0.03
      max_tokens: 8192
      capabilities: ["text-generation", "reasoning", "coding"]
  
  anthropic:
    claude-3:
      cost_per_1k_tokens: 0.015
      max_tokens: 200000
      capabilities: ["text-generation", "reasoning", "coding"]

monitoring:
  spike_threshold: 1000      # tokens per hour
  fraud_threshold: 10000     # tokens per hour
  alert_cooldown: 3600       # seconds

cost_optimization:
  free_tier_limits:
    gemini: 15000000         # tokens per month
    openai: 5000000          # tokens per month
    anthropic: 10000000      # tokens per month
    deepseek: 1000000        # tokens per month
```

---

## 🔍 Monitoring & Alerts

### 📊 **What Gets Monitored**

- **Token Usage**: Per user, per model, per hour/day
- **Cost Tracking**: Real-time cost analysis
- **Request Patterns**: Frequency and timing
- **Model Performance**: Response times and success rates

### 🚨 **Alert Types**

| Alert Type | Trigger | Severity |
|------------|---------|----------|
| **Usage Spike** | >1000 tokens/hour | Medium |
| **Fraud Detection** | >10000 tokens/hour | High |
| **Abnormal Pattern** | Unusual usage patterns | Medium |
| **Free Tier Limit** | Approaching limits | Low |

---

## 🧪 Development

### 🧪 **Running Tests**

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run all tests
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

### 🔧 **Adding New Models**

1. **Create Model Adapter** in `src/models/`
2. **Inherit from BaseAIModel**
3. **Implement required methods**
4. **Add configuration** to `config.yaml`
5. **Update ModelManager**

### 🚀 **Adding New Services**

1. **Create service** in `src/services/`
2. **Inherit from LoggerMixin**
3. **Add to API routes** if needed
4. **Update configuration**

---

## 🐳 Deployment

### 🐳 **Docker Deployment**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "src.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

### 🌍 **Environment Variables**

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `REDIS_URL` | Redis connection string | ✅ |
| `OPENAI_API_KEY` | OpenAI API key | ❌ |
| `ANTHROPIC_API_KEY` | Anthropic API key | ❌ |
| `GOOGLE_API_KEY` | Google API key | ❌ |
| `DEEPSEEK_API_KEY` | DeepSeek API key | ❌ |
| `SENTRY_DSN` | Sentry DSN for error tracking | ❌ |
| `SECRET_KEY` | Secret key for security | ✅ |
| `ENVIRONMENT` | Environment (dev/prod) | ❌ |

---

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/amazing-feature`)
3. **Commit** your changes (`git commit -m 'Add amazing feature'`)
4. **Push** to the branch (`git push origin feature/amazing-feature`)
5. **Open** a Pull Request

### 📋 **Development Guidelines**

- Write tests for new features
- Follow PEP 8 style guidelines
- Update documentation as needed
- Add type hints to new functions

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support & Help

### 📞 **Getting Help**

- **📖 Documentation**: Check `/docs` endpoint for API documentation
- **🐛 Issues**: Create an issue on GitHub
- **💬 Discussions**: Use GitHub Discussions
- **📧 Email**: Contact the maintainers

### 🔗 **Useful Links**

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic API Documentation](https://docs.anthropic.com/)
- [Google AI Documentation](https://ai.google.dev/)

---

## 🗺️ Roadmap

### 🚧 **Upcoming Features**

- [ ] **More AI Providers** (Cohere, Perplexity, etc.)
- [ ] **Advanced Prompt Templates** with variables
- [ ] **User Management** and authentication
- [ ] **Web Dashboard** for monitoring
- [ ] **Streaming Responses** support
- [ ] **A/B Testing** for model selection
- [ ] **Prompt Versioning** and history
- [ ] **Batch Processing** for multiple requests

### 🎯 **Performance Goals**

- [ ] **Sub-100ms** response times
- [ ] **99.9% uptime** SLA
- [ ] **Auto-scaling** support
- [ ] **Multi-region** deployment

---

<div align="center">

**Made with ❤️ for the AI community**

[![GitHub stars](https://img.shields.io/github/stars/yourusername/hapivet-prompt-library?style=social)](https://github.com/yourusername/hapivet-prompt-library)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/hapivet-prompt-library?style=social)](https://github.com/yourusername/hapivet-prompt-library)

</div>
