#!/bin/bash
# MoneyMind Startup Script

set -e

echo "🚀 Starting MoneyMind Finance AI Agent..."

# Check if .env exists
if [ ! -f backend/.env ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp backend/.env.example backend/.env
    echo "📝 Please edit backend/.env with your API keys before running!"
fi

# Start all services
echo "🐳 Starting Docker containers..."
docker-compose up -d

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check Ollama and pull model
echo "🤖 Checking Ollama..."
if docker exec moneymind-ollama ollama list 2>/dev/null | grep -q "gemma"; then
    echo "✅ Gemma model already exists"
else
    echo "📥 Pulling Gemma model (this may take a while)..."
    docker exec moneymind-ollama ollama pull gemma3:2b
fi

# Run database migrations
echo "🗄️  Running database migrations..."
docker exec moneymind-backend alembic upgrade head

# Initialize Neo4j knowledge graph
echo "🧠 Initializing knowledge graph..."
docker exec moneymind-backend python -c "
from src.application.services.intent_router import intent_router
import asyncio
asyncio.run(intent_router.initialize_knowledge_graph())
print('✅ Knowledge graph initialized')
"

echo ""
echo "✅ MoneyMind is ready!"
echo ""
echo "📍 Frontend:    http://localhost:3000"
echo "📍 Backend:     http://localhost:8000"
echo "📍 API Docs:    http://localhost:8000/docs"
echo "📍 Neo4j:       http://localhost:7474"
echo "📍 RabbitMQ:    http://localhost:15672"
echo ""
echo "🔌 WebSocket:   ws://localhost:8000/ws/chat"
