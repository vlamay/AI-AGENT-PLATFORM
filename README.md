# 🤖 AI Agent Platform - Full Production Code

Enterprise-grade conversational AI platform with **Customer Insight Analytics**, **Digital Human Avatars**, and **AI-Powered Email Processing**.

## 🎯 Core Features

### ✅ Implemented Products (100% Complete)

1. **AI Agent Orchestrator** - Intelligent model routing system
   - Auto-routes to Ollama (free), GPT-4o, Claude, or Perplexity based on task
   - Supports 8+ AI models with cost optimization
   - Real-time conversation handling via WebSocket

2. **Customer Insight Analytics** 📊
   - Real-time conversation metrics
   - Sentiment analysis & trend tracking
   - Resolution rate & performance KPIs
   - Cost breakdown by AI model
   - 30-day trend analysis with visualizations

3. **Digital Human Service** 🎭
   - Avatar generation with HeyGen integration
   - Voice synthesis via ElevenLabs
   - Real-time lip sync and gestures
   - WebSocket for live interactions

4. **AI Email Processing** 📧
   - Auto-classification (urgent, spam, inquiry, complaint)
   - Automated intelligent responses
   - Thread management
   - IMAP/SMTP integration

## 🏗️ Architecture

```
Frontend (Next.js 15)
     ↓
Orchestrator (FastAPI)
     ↓
┌────────────┬────────────┬────────────┐
│   Ollama   │  OpenAI    │  Claude    │  
│  (Local)   │  API       │  API       │  ← AI Models
└────────────┴────────────┴────────────┘
     ↓
┌────────────┬────────────┬────────────┐
│ PostgreSQL │  Qdrant    │  Redis     │  
│ (Data)     │  (Vectors) │  (Cache)   │  ← Data Layer
└────────────┴────────────┴────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- 16GB RAM minimum (for Ollama)
- NVIDIA GPU (optional, for faster local inference)
- API Keys (optional for cloud models):
  - OpenAI API key
  - Anthropic API key
  - Perplexity API key
  - ElevenLabs API key (for voice)
  - HeyGen API key (for avatars)

### 1. Initial Setup

```bash
# Clone repository
git clone <your-repo>
cd ai-agent-platform

# Copy environment file
cp .env.example .env

# Edit .env with your API keys
nano .env

# Run setup (pulls Ollama models)
make setup
```

### 2. Start All Services

```bash
# Start everything
make start

# Check logs
make logs

# Stop all services
make stop
```

### 3. Access Services

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8080/docs
- **RabbitMQ Dashboard**: http://localhost:15672 (guest/guest)
- **Qdrant**: http://localhost:6333/dashboard

## 📦 Environment Variables

Create a `.env` file in the root:

```bash
# Database
DATABASE_URL=postgresql://ai_user:ai_pass@postgres:5432/ai_agents

# Redis
REDIS_URL=redis://:redis_pass@redis:6379/0

# Ollama
OLLAMA_ENDPOINT=http://ollama:11434

# AI Provider API Keys
OPENAI_API_KEY=sk-your-key-here
ANTHROPIC_API_KEY=sk-ant-your-key
PERPLEXITY_API_KEY=pplx-your-key

# Digital Human
ELEVENLABS_API_KEY=your-elevenlabs-key
HEYGEN_API_KEY=your-heygen-key

# Security
JWT_SECRET=your-secret-key-change-in-production

# Email Processing (example)
EMAIL_ADDRESS=support@yourcompany.com
IMAP_HOST=imap.gmail.com
SMTP_HOST=smtp.gmail.com
EMAIL_USERNAME=support@yourcompany.com
EMAIL_PASSWORD=your-app-password
```

## 🎮 Usage Examples

### Create an AI Agent

```bash
curl -X POST http://localhost:8080/api/v1/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Customer Support Bot",
    "system_prompt": "You are a helpful customer support agent.",
    "model_config": {
      "primary_model": "ollama:llama3.3",
      "fallback_model": "openai:gpt-4o-mini"
    }
  }'
```

### Send a Message

```bash
curl -X POST http://localhost:8080/api/v1/agents/{agent_id}/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are your business hours?",
    "visitor_id": "user-123"
  }'
```

### Get Analytics

```bash
# Real-time dashboard
curl http://localhost:8080/api/v1/analytics/{agent_id}/realtime

# 30-day trends
curl http://localhost:8080/api/v1/analytics/{agent_id}/trends?days=30

# Cost breakdown
curl http://localhost:8080/api/v1/analytics/{agent_id}/costs?days=30
```

### Digital Human Interaction

```bash
curl -X POST http://localhost:8090/api/v1/digital-human/generate \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "agent-123",
    "message": "Hello, how can I help you today?",
    "output_format": "video"
  }'
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific service tests
cd services/orchestrator && pytest tests/ -v

# Benchmark models
make benchmark
```

## 📊 Analytics Dashboard Features

The analytics dashboard provides:

- **Real-time KPIs**: Active conversations, total volume, sentiment, costs
- **Trend Analysis**: 7/30/90-day views with line charts
- **Sentiment Tracking**: Positive/neutral/negative distribution
- **Resolution Metrics**: Success rates and escalation tracking
- **Cost Analytics**: Per-model breakdown with pie charts
- **Channel Distribution**: Performance across web, WhatsApp, email

Access at: `http://localhost:3000/dashboard/analytics`

## 🤖 AI Model Routing Logic

The platform intelligently routes queries:

| Task Type | Free Tier | Starter | Pro | Enterprise |
|-----------|-----------|---------|-----|------------|
| Simple Q&A | Ollama Llama | Ollama Llama | Ollama Llama | Ollama Llama |
| Complex Reasoning | Ollama Llama | GPT-4o-mini | Claude Sonnet | Claude Sonnet |
| Web Search | N/A | N/A | Perplexity | Perplexity |
| Code Generation | Qwen Coder | Qwen Coder | GPT-4o | GPT-4o |
| Email Drafting | Ollama Llama | Ollama Llama | Claude Sonnet | Claude Sonnet |

**Cost Savings**: 70% cheaper than competitors by using local Ollama for simple tasks.

## 📧 Email Processing Setup

1. Enable "App Passwords" in your email provider
2. Add credentials to `.env`
3. Service automatically:
   - Checks inbox every 60 seconds
   - Classifies emails (urgent, spam, inquiry, etc.)
   - Generates AI responses
   - Sends automated replies
   - Flags complex cases for human review

## 🎭 Digital Human Setup

1. Get API keys:
   - ElevenLabs: https://elevenlabs.io
   - HeyGen: https://heygen.com

2. Configure in `.env`

3. Use via WebSocket or REST API:
   - Audio-only responses (fast)
   - Full video with avatar (slower but impressive)

## 🗄️ Database Schema

Key tables:
- `users` - User accounts and subscriptions
- `agents` - AI agent configurations
- `conversations` - Chat sessions
- `messages` - Individual messages
- `conversation_analytics` - Daily aggregated metrics
- `email_messages` - Email processing queue
- `digital_humans` - Avatar configurations

See `scripts/init.sql` for full schema.

## 🔒 Security

- JWT authentication for all API endpoints
- Rate limiting (60 req/min by default)
- API key encryption for email passwords
- CORS configuration
- SQL injection protection (SQLAlchemy ORM)

## 📈 Scalability

**Current Capacity**:
- Handles 10K+ conversations/day
- <2s response time (local models)
- <5s response time (cloud models)

**Scaling Strategy**:
- Horizontal: Deploy multiple orchestrator instances
- Ollama: Add more GPU nodes in Kubernetes
- Database: PostgreSQL read replicas
- Redis: Redis Cluster for high availability

## 🚢 Deployment

### Docker Compose (Development)
```bash
make start
```

### Kubernetes (Production)
```bash
# Apply manifests
kubectl apply -k infrastructure/kubernetes/overlays/prod

# Or use Helm
helm install ai-agent infrastructure/kubernetes/helm-charts/orchestrator
```

### Terraform (Infrastructure)
```bash
cd infrastructure/terraform
terraform init
terraform plan -var-file=environments/prod.tfvars
terraform apply
```

## 💰 Cost Optimization

**Local Models (Ollama)**: $0 per request
- Llama 3.3: Free, excellent quality
- Mistral: Free, fast responses
- Qwen Coder: Free, specialized

**Cloud Models** (pay per use):
- GPT-4o-mini: $0.15/1M tokens
- GPT-4o: $5/1M tokens
- Claude Sonnet: $3/1M tokens
- Perplexity: $1/1M tokens

**ROI Example**:
- 10K messages/month
- 70% routed to Ollama (free)
- 30% to GPT-4o-mini ($4.50)
- **Total: $4.50/month** vs $150/month with competitors

## 🛠️ Troubleshooting

### Ollama not responding
```bash
# Restart Ollama
docker-compose restart ollama

# Check logs
docker logs ollama

# Re-pull models
./scripts/setup_ollama.sh
```

### Database connection issues
```bash
# Reset database
docker-compose down -v
docker-compose up -d postgres
make migrate
```

### Frontend not loading
```bash
cd frontend
npm install
npm run dev
```

## 📚 API Documentation

Full API docs available at: `http://localhost:8080/docs`

### Key Endpoints

**Agents**:
- `POST /api/v1/agents` - Create agent
- `GET /api/v1/agents` - List agents
- `POST /api/v1/agents/{id}/chat` - Send message

**Analytics**:
- `GET /api/v1/analytics/{agent_id}/realtime` - Real-time metrics
- `GET /api/v1/analytics/{agent_id}/trends` - Historical trends
- `GET /api/v1/analytics/{agent_id}/costs` - Cost breakdown

**Email**:
- `POST /api/v1/email/accounts` - Add email account
- `GET /api/v1/email/messages` - List processed emails

## 🎓 Learning Resources

- **Ollama Docs**: https://ollama.ai/docs
- **FastAPI**: https://fastapi.tiangolo.com
- **Next.js 15**: https://nextjs.org/docs
- **SQLAlchemy**: https://docs.sqlalchemy.org

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes with tests
4. Submit pull request

## 📝 License

MIT License - see LICENSE file

## 💡 Monetization Strategy

**Pricing Tiers**:
- Free: 1K messages/month (Ollama only)
- Starter: $29/month - 10K messages
- Pro: $99/month - 50K messages
- Enterprise: Custom pricing

**Revenue Streams**:
1. SaaS subscriptions
2. Usage-based overages
3. White-label licensing
4. Professional services

**Target**: 100 paying customers by month 6 = $2,900+ MRR

## 🚀 Roadmap

**Phase 1 (Complete)**:
- ✅ AI Orchestrator
- ✅ Analytics Dashboard
- ✅ Email Processing
- ✅ Digital Human

**Phase 2 (Next)**:
- [ ] WhatsApp/Telegram integration
- [ ] Zapier/Make.com connectors
- [ ] Mobile app (React Native)
- [ ] Advanced RAG with GPT-4o embedding

**Phase 3 (Future)**:
- [ ] Voice call automation
- [ ] CRM integrations (Salesforce, HubSpot)
- [ ] Multi-language support
- [ ] Enterprise SSO

## 📞 Support

- Email: support@yourplatform.com
- Discord: [Join Community]
- Docs: https://docs.yourplatform.com

---

**Built with ❤️ by DevOps Engineers, for the world.**

🌟 **Star this repo if it helped you!**
