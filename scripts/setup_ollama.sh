#!/bin/bash

echo "🤖 AI Agent Platform - Ollama Setup"
echo "===================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start Ollama container if not running
if ! docker ps | grep -q ollama; then
    echo "📦 Starting Ollama container..."
    docker compose up -d ollama
    sleep 5
fi

echo "📥 Pulling AI models..."

# Pull Llama 3.3 (8B parameters - excellent for general tasks)
echo "⬇️  Pulling Llama 3.3 (8B)..."
docker exec ollama ollama pull llama3.3:latest

# Pull Mistral (7B parameters - fast and efficient)
echo "⬇️  Pulling Mistral (7B)..."
docker exec ollama ollama pull mistral:latest

# Pull Qwen2.5-Coder (specialized for code generation)
echo "⬇️  Pulling Qwen2.5-Coder (7B)..."
docker exec ollama ollama pull qwen2.5-coder:latest

echo "✅ All models downloaded successfully!"

# Test models
echo ""
echo "🧪 Testing models..."

echo "Testing Llama 3.3..."
docker exec ollama ollama run llama3.3 "Say 'Hello from Llama 3.3!'" --verbose=false

echo "Testing Mistral..."
docker exec ollama ollama run mistral "Say 'Hello from Mistral!'" --verbose=false

echo "Testing Qwen2.5-Coder..."
docker exec ollama ollama run qwen2.5-coder "Say 'Hello from Qwen Coder!'" --verbose=false

echo ""
echo "✅ Setup complete! All models are ready."
echo ""
echo "📊 Model information:"
docker exec ollama ollama list

echo ""
echo "🚀 You can now start the full platform with:"
echo "   make start"
