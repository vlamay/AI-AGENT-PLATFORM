#!/bin/bash

# ============================================
# AI Agent Platform - Validation & Startup Script
# ============================================

set -e

echo "🚀 AI AGENT PLATFORM - VALIDATION & STARTUP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Check Docker
echo "📦 Step 1: Checking Docker..."
if command -v docker &> /dev/null; then
    DOCKER_VERSION=$(docker --version)
    echo -e "${GREEN}✅ Docker installed: $DOCKER_VERSION${NC}"
else
    echo -e "${RED}❌ Docker not found. Install with: sudo apt install docker.io${NC}"
    exit 1
fi

# Step 2: Check Docker Compose
echo ""
echo "📦 Step 2: Checking Docker Compose..."
if command -v docker &> /dev/null && docker compose version &> /dev/null; then
    COMPOSE_VERSION=$(docker compose version)
    echo -e "${GREEN}✅ Docker Compose installed: $COMPOSE_VERSION${NC}"
    COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    COMPOSE_VERSION=$(docker-compose --version)
    echo -e "${GREEN}✅ Docker Compose installed: $COMPOSE_VERSION${NC}"
    COMPOSE_CMD="docker-compose"
else
    echo -e "${RED}❌ Docker Compose not found. Install with: sudo apt install docker-compose${NC}"
    exit 1
fi

# Step 3: Check system resources
echo ""
echo "💻 Step 3: Checking system resources..."
TOTAL_MEM=$(free -g | awk '/^Mem:/{print $2}')
if [ $TOTAL_MEM -ge 16 ]; then
    echo -e "${GREEN}✅ RAM: ${TOTAL_MEM}GB (sufficient)${NC}"
else
    echo -e "${YELLOW}⚠️  RAM: ${TOTAL_MEM}GB (recommend 16GB+)${NC}"
fi

# Step 4: Check if ports are available
echo ""
echo "🔌 Step 4: Checking port availability..."
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${RED}❌ Port $port is already in use${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Port $port is available${NC}"
        return 0
    fi
}

check_port 11434 && PORTS_OK=$((PORTS_OK + 0))
check_port 5433 && PORTS_OK=$((PORTS_OK + 0))
check_port 6379 && PORTS_OK=$((PORTS_OK + 0))
check_port 5678 && PORTS_OK=$((PORTS_OK + 0))
check_port 3001 && PORTS_OK=$((PORTS_OK + 0))

# Step 5: Check NVIDIA GPU (optional)
echo ""
echo "🎮 Step 5: Checking NVIDIA GPU..."
if command -v nvidia-smi &> /dev/null; then
    GPU_INFO=$(nvidia-smi --query-gpu=name --format=csv,noheader,nounits 2>/dev/null | head -1)
    if [ ! -z "$GPU_INFO" ]; then
        echo -e "${GREEN}✅ NVIDIA GPU detected: $GPU_INFO${NC}"
        echo -e "${YELLOW}💡 Tip: Uncomment GPU settings in docker-compose for better performance${NC}"
    else
        echo -e "${YELLOW}⚠️  nvidia-smi found but no GPU detected${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  NVIDIA drivers not installed (optional, CPU mode available)${NC}"
fi

# Step 6: Pull Docker images
echo ""
echo "📥 Step 6: Pulling Docker images..."
echo "This may take a few minutes..."
$COMPOSE_CMD -f docker-compose-minimal.yml pull

# Step 7: Start services
echo ""
echo "🚀 Step 7: Starting AI Agent Platform..."
$COMPOSE_CMD -f docker-compose-minimal.yml up -d

# Step 8: Wait for services to be healthy
echo ""
echo "⏳ Step 8: Waiting for services to be ready..."
sleep 10

# Step 9: Check service status
echo ""
echo "📊 Step 9: Service status:"
$COMPOSE_CMD -f docker-compose-minimal.yml ps

# Step 10: Install Ollama models
echo ""
echo "🤖 Step 10: Installing Ollama models..."
echo "Pulling Llama 3.3 (this will take 10-15 minutes)..."
docker exec -it ai-platform-ollama ollama pull llama3.3 || echo "⚠️  Llama 3.3 pull failed, continuing..."

echo ""
echo "Pulling Qwen2.5 for code generation..."
docker exec -it ai-platform-ollama ollama pull qwen2.5:7b || echo "⚠️  Qwen2.5 pull failed, continuing..."

# Step 11: Test services
echo ""
echo "🧪 Step 11: Testing services..."

# Test Ollama
echo "Testing Ollama..."
sleep 5
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Ollama is running${NC}"
else
    echo -e "${RED}❌ Ollama is not responding${NC}"
fi

# Test PostgreSQL
echo "Testing PostgreSQL..."
if docker exec -it ai-platform-db pg_isready -U postgres > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL is running${NC}"
else
    echo -e "${RED}❌ PostgreSQL is not responding${NC}"
fi

# Test Redis
echo "Testing Redis..."
if docker exec -it ai-platform-redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis is running${NC}"
else
    echo -e "${RED}❌ Redis is not responding${NC}"
fi

# Test n8n
echo "Testing n8n..."
sleep 5
if curl -s http://localhost:5678/healthz > /dev/null 2>&1; then
    echo -e "${GREEN}✅ n8n is running${NC}"
else
    echo -e "${RED}❌ n8n is not responding${NC}"
fi

# Final summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 AI AGENT PLATFORM IS READY!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Access URLs:"
echo "   • Ollama API: http://localhost:11434"
echo "   • n8n UI: http://localhost:5678"
echo "     Login: admin / ai_platform_2024"
echo "   • Grafana: http://localhost:3001"
echo "     Login: admin / admin"
echo ""
echo "🔧 Useful commands:"
echo "   • View logs: docker compose -f docker-compose-minimal.yml logs -f"
echo "   • Stop all: docker compose -f docker-compose-minimal.yml down"
echo "   • Restart: docker compose -f docker-compose-minimal.yml restart"
echo ""
echo "🤖 Test Ollama:"
echo '   curl http://localhost:11434/api/generate -d '"'"'{"model": "llama3.3", "prompt": "Hello", "stream": false}'"'"''
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

