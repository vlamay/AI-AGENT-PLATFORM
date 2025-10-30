# 🚀 QUICK START GUIDE - AI Agent Platform

## ⚡ 5-Minute Setup (No API Keys Needed)

### Step 1: Clone & Setup (1 minute)

```bash
# Navigate to your projects folder
cd ~/projects

# The code is already generated at:
cd /home/claude/ai-agent-platform

# Make scripts executable
chmod +x scripts/*.sh

# Copy environment file
cp .env.example .env
```

### Step 2: Start Services (2 minutes)

```bash
# Pull and setup Ollama models (takes ~2 min)
./scripts/setup_ollama.sh

# Start all services
docker-compose up -d

# Watch logs (optional)
docker-compose logs -f
```

### Step 3: Verify Everything Works (2 minutes)

```bash
# Check all containers are running
docker-compose ps

# Test Ollama
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.3",
  "prompt": "Say hello!",
  "stream": false
}'

# Check API health
curl http://localhost:8080/health

# Access frontend
open http://localhost:3000
```

---

## 🎮 DEMO SCENARIOS

### Scenario 1: Send Your First Message

```bash
# Create an agent
curl -X POST http://localhost:8080/api/v1/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo Support Bot",
    "system_prompt": "You are a helpful customer support agent.",
    "model_config": {
      "primary_model": "ollama:llama3.3"
    }
  }'

# Save the returned agent_id, then:
export AGENT_ID="<your-agent-id>"

# Send a message
curl -X POST "http://localhost:8080/api/v1/agents/$AGENT_ID/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What are your business hours?",
    "visitor_id": "demo-user-123"
  }'
```

### Scenario 2: View Analytics

```bash
# Get real-time metrics
curl "http://localhost:8080/api/v1/analytics/$AGENT_ID/realtime" | jq

# Get 7-day trends
curl "http://localhost:8080/api/v1/analytics/$AGENT_ID/trends?days=7" | jq

# Get cost breakdown
curl "http://localhost:8080/api/v1/analytics/$AGENT_ID/costs?days=7" | jq
```

### Scenario 3: Test Email Processing

```bash
# Add your email account
curl -X POST http://localhost:8080/api/v1/email/accounts \
  -H "Content-Type: application/json" \
  -d '{
    "email_address": "support@yourcompany.com",
    "imap_host": "imap.gmail.com",
    "imap_port": 993,
    "smtp_host": "smtp.gmail.com",
    "smtp_port": 587,
    "username": "support@yourcompany.com",
    "password": "your-app-password",
    "agent_id": "'$AGENT_ID'"
  }'

# Email processor will start checking inbox automatically
docker-compose logs -f email-processor
```

### Scenario 4: Try Digital Human

```bash
# Generate audio response
curl -X POST http://localhost:8090/api/v1/digital-human/generate \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": "'$AGENT_ID'",
    "message": "Hello, welcome to our platform!",
    "output_format": "audio"
  }'

# Note: Requires ELEVENLABS_API_KEY in .env for voice
```

---

## 🔑 Adding API Keys (Optional)

Edit `.env` file:

```bash
nano .env
```

Add your keys:

```bash
# For better responses
OPENAI_API_KEY=sk-proj-your-key-here

# For complex reasoning
ANTHROPIC_API_KEY=sk-ant-your-key-here

# For web search
PERPLEXITY_API_KEY=pplx-your-key-here

# For digital human voice
ELEVENLABS_API_KEY=your-elevenlabs-key
```

Restart services:

```bash
docker-compose restart orchestrator digital-human
```

---

## 📊 Access Dashboards

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | - |
| API Docs | http://localhost:8080/docs | - |
| RabbitMQ | http://localhost:15672 | guest/guest |
| Qdrant | http://localhost:6333/dashboard | - |

---

## 🧪 Testing Different Models

### Test Ollama Llama 3.3
```bash
curl -X POST "http://localhost:8080/api/v1/agents/$AGENT_ID/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Explain quantum computing in simple terms",
    "force_model": "ollama:llama3.3"
  }'
```

### Test Code Generation (Qwen)
```bash
curl -X POST "http://localhost:8080/api/v1/agents/$AGENT_ID/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Write a Python function to calculate fibonacci numbers",
    "force_model": "ollama:qwen2.5"
  }'
```

### Test GPT-4o-mini (needs API key)
```bash
curl -X POST "http://localhost:8080/api/v1/agents/$AGENT_ID/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Analyze the pros and cons of remote work",
    "force_model": "openai:gpt-4o-mini"
  }'
```

---

## 📈 Load Testing

Generate 100 conversations:

```bash
# Install hey (HTTP load testing)
go install github.com/rakyll/hey@latest

# Load test the chat endpoint
hey -n 100 -c 10 -m POST \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","visitor_id":"load-test"}' \
  "http://localhost:8080/api/v1/agents/$AGENT_ID/chat"
```

Expected results:
- Requests/sec: 20-30 (local Ollama)
- Response time: 1-3 seconds (P95)
- Success rate: 100%

---

## 🐛 Debugging Tips

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f orchestrator
docker-compose logs -f ollama

# Search logs
docker-compose logs orchestrator | grep ERROR
```

### Check Resource Usage
```bash
# Docker stats
docker stats

# PostgreSQL queries
docker-compose exec postgres psql -U ai_user -d ai_agents -c "
  SELECT * FROM conversations ORDER BY started_at DESC LIMIT 10;
"
```

### Reset Everything
```bash
# Stop and remove all data
docker-compose down -v

# Restart fresh
./scripts/setup_ollama.sh
docker-compose up -d
```

---

## 🎯 Next Steps

1. **Customize Your Agent**
   - Edit system prompts
   - Add knowledge base documents
   - Configure routing preferences

2. **Build Integrations**
   - Connect WhatsApp/Telegram
   - Setup webhooks
   - Integrate with your CRM

3. **Deploy to Production**
   ```bash
   cd infrastructure/terraform
   terraform init
   terraform apply -var-file=environments/prod.tfvars
   ```

4. **Monetize**
   - Setup Stripe billing
   - Create pricing tiers
   - Launch marketing site

---

## 💡 Pro Tips

**Optimize Costs**:
```bash
# Set aggressive local routing in .env
DEFAULT_MODEL=ollama:llama3.3
FALLBACK_TO_CLOUD=false
```

**Speed Up Ollama**:
```bash
# Use GPU acceleration
docker-compose -f docker-compose.gpu.yml up -d ollama
```

**Enable Debug Mode**:
```bash
# In .env
DEBUG=true
LOG_LEVEL=DEBUG
```

**Monitor Performance**:
```bash
# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack
```

---

## 📞 Get Help

**Issues?**
- GitHub Issues: [Create Issue]
- Discord: [Join Community]
- Email: support@yourplatform.com

**Resources**:
- Full Docs: `/README.md`
- Architecture: `/ARCHITECTURE.md`
- API Reference: `http://localhost:8080/docs`

---

## ✅ Checklist Before Going Live

- [ ] All tests pass: `make test`
- [ ] Environment variables secured
- [ ] SSL/HTTPS configured
- [ ] Monitoring setup (Prometheus/Grafana)
- [ ] Backup strategy for PostgreSQL
- [ ] Rate limiting configured
- [ ] Cost alerts setup
- [ ] Documentation updated
- [ ] Legal pages (ToS, Privacy Policy)
- [ ] Support channels ready

---

**🎉 Congratulations! Your AI Agent Platform is ready to scale.**

**Time to first conversation: <5 minutes**  
**Time to first paying customer: <30 days**  
**Target revenue: $5K MRR by month 6**

**Let's build something amazing! 🚀**
