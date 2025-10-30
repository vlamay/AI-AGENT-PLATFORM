"""
AI Agent Platform - Main Orchestrator API
FastAPI-based routing service for intelligent AI model selection
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging

from app.core.config import settings
from app.core.router import IntelligentRouter, TaskType
from app.services.model_clients import ModelClientFactory, ModelProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global state
router_cache = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 AI Agent Orchestrator starting up...")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    yield
    # Shutdown
    logger.info("🛑 Shutting down...")

app = FastAPI(
    title="AI Agent Platform - Orchestrator",
    description="Intelligent AI model routing and conversation management",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "name": "AI Agent Platform",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "orchestrator",
        "environment": settings.ENVIRONMENT
    }

# API Routes
from pydantic import BaseModel
from typing import Optional, List, Dict
import uuid

class ChatRequest(BaseModel):
    agent_id: str
    message: str
    visitor_id: str
    channel: str = "web"
    conversation_id: Optional[str] = None
    metadata: Optional[Dict] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: str
    model_used: str
    confidence: float
    cost_usd: float
    latency_ms: int

@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, background_tasks: BackgroundTasks):
    """
    Main chat endpoint - intelligent AI routing
    """
    logger.info(f"Processing chat request for agent: {request.agent_id}")
    
    try:
        # Get router for this agent
        intelligent_router = IntelligentRouter(
            user_tier="pro",  # TODO: Fetch from database
            conversation_context={}
        )
        
        # Make routing decision
        decision = intelligent_router.route(request.message)
        logger.info(f"Routing decision: {decision.provider.value} ({decision.confidence})")
        
        # Get model client
        client = ModelClientFactory.get_client(decision.provider)
        
        # Generate response
        response = await client.generate(
            prompt=request.message,
            agent_id=request.agent_id,
            conversation_id=request.conversation_id or str(uuid.uuid4())
        )
        
        # TODO: Save to database
        # background_tasks.add_task(save_conversation, ...)
        
        return ChatResponse(
            response=response.text,
            conversation_id=request.conversation_id or str(uuid.uuid4()),
            model_used=response.model,
            confidence=decision.confidence,
            cost_usd=response.cost_usd,
            latency_ms=response.latency_ms
        )
        
    except Exception as e:
        logger.error(f"Error processing chat: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

class AgentCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    user_id: str

class AgentResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    created_at: str

@app.post("/api/v1/agents", response_model=AgentResponse)
async def create_agent(request: AgentCreateRequest):
    """Create a new AI agent"""
    # TODO: Save to database
    agent_id = str(uuid.uuid4())
    
    return AgentResponse(
        id=agent_id,
        name=request.name,
        description=request.description,
        created_at="2024-01-01T00:00:00Z"
    )

@app.get("/api/v1/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get agent details"""
    # TODO: Fetch from database
    return {
        "id": agent_id,
        "name": "Demo Agent",
        "status": "active"
    }

@app.get("/api/v1/agents/{agent_id}/analytics")
async def get_analytics(agent_id: str, days: int = 30):
    """Get conversation analytics for agent"""
    # TODO: Implement analytics query
    return {
        "agent_id": agent_id,
        "period_days": days,
        "total_conversations": 0,
        "avg_sentiment": 0.5
    }

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )

