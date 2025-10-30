#!/bin/bash

# ============================================
# AI AGENT PLATFORM - QUICK DEPLOYMENT
# ============================================

set -e

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  🚀 AI AGENT PLATFORM - QUICK DEPLOYMENT                ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not installed. Install first: sudo apt install docker.io docker-compose"
    exit 1
fi

# Check Docker Compose
if ! docker compose version &> /dev/null 2>&1; then
    echo "❌ Docker Compose not installed"
    exit 1
fi

echo "✅ Docker ready"
echo ""

# Start minimal stack
echo "📦 Starting minimal stack..."
docker compose -f docker-compose-minimal.yml up -d

echo "⏳ Waiting for services to start (30 seconds)..."
sleep 30

# Install Ollama models
echo "🤖 Installing Ollama models..."
docker exec -it ai-platform-ollama ollama pull llama3.3 || true
docker exec -it ai-platform-ollama ollama pull qwen2.5:7b || true

# Check services
echo ""
echo "📊 Service Status:"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "ai-platform"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ✅ DEPLOYMENT COMPLETE                                 ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "📝 Access URLs:"
echo "   • n8n:    http://localhost:5678 (admin / ai_platform_2024)"
echo "   • Grafana: http://localhost:3001 (admin / admin)"
echo ""
echo "🧪 Test Ollama:"
echo '   curl http://localhost:11434/api/generate -d '"'"'{"model":"llama3.3","prompt":"Hello","stream":false}'"'"''
echo ""

