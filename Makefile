.PHONY: help setup start stop restart logs clean test

help:
	@echo "AI Agent Platform - Development Commands"
	@echo ""
	@echo "  make setup       - Initialize project and pull Ollama models"
	@echo "  make start       - Start all services with docker-compose"
	@echo "  make stop        - Stop all services"
	@echo "  make restart     - Restart all services"
	@echo "  make logs        - Show logs from all services"
	@echo "  make logs-{svc}  - Show logs from specific service"
	@echo "  make clean       - Remove all containers and volumes"
	@echo "  make test        - Run tests"
	@echo "  make migrate     - Run database migrations"

setup:
	@echo "🚀 Setting up AI Agent Platform..."
	@chmod +x scripts/*.sh
	@./scripts/setup_ollama.sh
	@echo "✅ Setup complete!"

start:
	@echo "🚀 Starting all services..."
	docker-compose up -d
	@echo "✅ Services started!"
	@echo ""
	@echo "Access your platform:"
	@echo "  Frontend:   http://localhost:3000"
	@echo "  API Docs:   http://localhost:8080/docs"
	@echo "  RabbitMQ:   http://localhost:15672 (guest/guest)"
	@echo "  Qdrant:     http://localhost:6333"

stop:
	@echo "🛑 Stopping all services..."
	docker-compose down

restart:
	@echo "🔄 Restarting all services..."
	docker-compose restart

logs:
	docker-compose logs -f

logs-orchestrator:
	docker-compose logs -f orchestrator

logs-ollama:
	docker-compose logs -f ollama

logs-frontend:
	docker-compose logs -f frontend

clean:
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	@echo "✅ Cleanup complete!"

test:
	@echo "🧪 Running tests..."
	cd services/orchestrator && pytest tests/ -v

migrate:
	@echo "📊 Running migrations..."
	docker-compose exec postgres psql -U ai_user -d ai_agents -f /docker-entrypoint-initdb.d/init.sql

ps:
	docker-compose ps

