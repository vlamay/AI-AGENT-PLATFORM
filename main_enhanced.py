"""
AI Agent Platform - Production FastAPI Orchestrator
Provides REST API for AI model routing with monitoring and analytics
"""
import os
import time
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
import httpx
from prometheus_client import Counter, Histogram, generate_latest

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="AI Agent Platform API",
    description="Production-ready AI orchestration with intelligent routing",
    version="1.0.0",
    docs_url="/",
    redoc_url="/redoc"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
REQUEST_COUNT = Counter('api_requests_total', 'Total API requests', ['endpoint', 'method'])
REQUEST_DURATION = Histogram('api_request_duration_seconds', 'Request duration')
MODEL_USAGE = Counter('model_usage_total', 'Model usage count', ['model'])
TOKEN_USAGE = Counter('token_usage_total', 'Token usage', ['model', 'type'])

# Environment variables
OLLAMA_ENDPOINT = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")

# ============================================
# MODELS
# ============================================

class ChatRequest(BaseModel):
    """Request model for chat completions"""
    prompt: str = Field(..., min_length=1, max_length=10000, description="User prompt")
    task_type: Optional[str] = Field(
        default="auto",
        description="Task type: auto, code, chat, complex, search"
    )
    model: Optional[str] = Field(
        default=None,
        description="Specific model to use (overrides auto-routing)"
    )
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=2000, ge=1, le=8000)
    stream: Optional[bool] = Field(default=False, description="Stream response")
    
    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Write a Python function to calculate Fibonacci numbers",
                "task_type": "code",
                "temperature": 0.1,
                "max_tokens": 1000
            }
        }

class ChatResponse(BaseModel):
    """Response model for chat completions"""
    model: str
    response: str
    task_type: str
    tokens_used: Optional[int] = None
    duration_ms: int
    timestamp: str
    cost_usd: Optional[float] = 0.0

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: str
    services: Dict[str, str]

# ============================================
# AI MODEL CLIENTS
# ============================================

class ModelRouter:
    """Intelligent routing between AI models"""
    
    # Model configurations with cost per 1M tokens
    MODELS = {
        "llama3.3": {"endpoint": "ollama", "cost_input": 0.0, "cost_output": 0.0},
        "qwen2.5-coder:7b": {"endpoint": "ollama", "cost_input": 0.0, "cost_output": 0.0},
        "mistral:7b": {"endpoint": "ollama", "cost_input": 0.0, "cost_output": 0.0},
        "gpt-4o": {"endpoint": "openai", "cost_input": 5.0, "cost_output": 15.0},
        "gpt-4o-mini": {"endpoint": "openai", "cost_input": 0.15, "cost_output": 0.6},
        "claude-sonnet-4-20250514": {"endpoint": "anthropic", "cost_input": 3.0, "cost_output": 15.0},
    }
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=120.0)
    
    async def route_request(self, request: ChatRequest) -> tuple[str, str]:
        """Intelligently route request to optimal model"""
        if request.model:
            if request.model not in self.MODELS:
                raise HTTPException(400, f"Model {request.model} not supported")
            return request.model, self.MODELS[request.model]["endpoint"]
        
        # Auto-routing based on task_type
        task_routes = {
            "code": "qwen2.5-coder:7b",
            "chat": "llama3.3",
            "complex": "gpt-4o-mini",
            "search": "llama3.3",
        }
        
        # Auto-detect if task_type is "auto"
        if request.task_type == "auto":
            prompt_lower = request.prompt.lower()
            if any(kw in prompt_lower for kw in ["code", "function", "script", "debug", "programming"]):
                request.task_type = "code"
            elif any(kw in prompt_lower for kw in ["search", "find", "latest", "news"]):
                request.task_type = "search"
            elif len(request.prompt) > 500:
                request.task_type = "complex"
            else:
                request.task_type = "chat"
        
        model = task_routes.get(request.task_type, "llama3.3")
        return model, self.MODELS[model]["endpoint"]
    
    async def call_ollama(self, model: str, prompt: str, **kwargs) -> Dict[str, Any]:
        """Call local Ollama API"""
        url = f"{OLLAMA_ENDPOINT}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": kwargs.get("stream", False),
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "num_predict": kwargs.get("max_tokens", 2000),
            }
        }
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return {
                "response": data.get("response", ""),
                "tokens": data.get("eval_count", 0),
                "model": model
            }
        except httpx.HTTPError as e:
            logger.error(f"Ollama API error: {e}")
            raise HTTPException(500, f"Ollama error: {str(e)}")
    
    def calculate_cost(self, model: str, tokens: int) -> float:
        """Calculate cost in USD"""
        if model not in self.MODELS:
            return 0.0
        config = self.MODELS[model]
        input_tokens = int(tokens * 0.6)
        output_tokens = int(tokens * 0.4)
        cost = (
            (input_tokens / 1_000_000) * config["cost_input"] +
            (output_tokens / 1_000_000) * config["cost_output"]
        )
        return round(cost, 6)

# Initialize router
router = ModelRouter()

# ============================================
# API ENDPOINTS
# ============================================

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    services = {}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_ENDPOINT}/api/tags", timeout=5.0)
            services["ollama"] = "healthy" if response.status_code == 200 else "unhealthy"
    except:
        services["ollama"] = "unavailable"
    services["openai"] = "configured" if OPENAI_API_KEY else "not_configured"
    services["anthropic"] = "configured" if ANTHROPIC_API_KEY else "not_configured"
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
        services=services
    )

@app.post("/v1/chat/completions", response_model=ChatResponse)
async def chat_completion(request: ChatRequest, background_tasks: BackgroundTasks):
    """Main chat completion endpoint with intelligent routing"""
    start_time = time.time()
    REQUEST_COUNT.labels(endpoint="/v1/chat/completions", method="POST").inc()
    try:
        model, endpoint = await router.route_request(request)
        logger.info(f"Routing to {model} ({endpoint}) for task_type={request.task_type}")
        MODEL_USAGE.labels(model=model).inc()
        
        if endpoint == "ollama":
            result = await router.call_ollama(
                model, request.prompt, 
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=request.stream
            )
        else:
            raise HTTPException(500, f"Cloud endpoint {endpoint} requires API key")
        
        duration_ms = int((time.time() - start_time) * 1000)
        cost = router.calculate_cost(model, result["tokens"])
        REQUEST_DURATION.observe(time.time() - start_time)
        TOKEN_USAGE.labels(model=model, type="total").inc(result["tokens"])
        
        return ChatResponse(
            model=model,
            response=result["response"],
            task_type=request.task_type,
            tokens_used=result["tokens"],
            duration_ms=duration_ms,
            timestamp=datetime.utcnow().isoformat(),
            cost_usd=cost
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(500, f"Internal error: {str(e)}")

@app.get("/v1/models")
async def list_models():
    """List available models"""
    return {
        "models": [
            {
                "id": model,
                "endpoint": config["endpoint"],
                "cost_per_1m_input": config["cost_input"],
                "cost_per_1m_output": config["cost_output"]
            }
            for model, config in router.MODELS.items()
        ]
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest()

@app.on_event("startup")
async def startup_event():
    logger.info("AI Agent Platform API starting...")
    logger.info(f"Ollama endpoint: {OLLAMA_ENDPOINT}")

@app.on_event("shutdown")
async def shutdown_event():
    await router.client.aclose()
    logger.info("AI Agent Platform API shutting down...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)

