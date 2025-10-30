from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Environment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # API Configuration
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "AI Agent Platform"
    
    # Database
    DATABASE_URL: str = "postgresql://ai_user:ai_pass@localhost:5432/ai_agents"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # RabbitMQ
    RABBITMQ_URL: str = "amqp://guest:guest@localhost:5672/"
    
    # Ollama
    OLLAMA_ENDPOINT: str = "http://localhost:11434"
    
    # Vector Database
    QDRANT_URL: str = "http://localhost:6333"
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    # Anthropic
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-sonnet-4"
    
    # Perplexity
    PERPLEXITY_API_KEY: Optional[str] = None
    PERPLEXITY_MODEL: str = "sonar-pro"
    
    # DeepSeek
    DEEPSEEK_API_KEY: Optional[str] = None
    
    # ElevenLabs (Voice)
    ELEVENLABS_API_KEY: Optional[str] = None
    
    # HeyGen (Digital Human)
    HEYGEN_API_KEY: Optional[str] = None
    
    # Security
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Model Routing Configuration
    OLLAMA_MODELS: list = [
        "llama3.3:latest",
        "mistral:latest",
        "qwen2.5-coder:latest"
    ]
    
    # Cost per 1K tokens (USD)
    MODEL_COSTS: dict = {
        "ollama:llama3.3": 0.0,
        "ollama:mistral": 0.0,
        "ollama:qwen2.5": 0.0,
        "openai:gpt-4o-mini": 0.00015,
        "openai:gpt-4o": 0.005,
        "anthropic:claude-sonnet-4": 0.003,
        "perplexity:sonar-pro": 0.001,
        "deepseek:deepseek-r1": 0.0005
    }
    
    # Email Processing
    EMAIL_PROCESSING_INTERVAL: int = 60  # seconds
    
    # Analytics
    ANALYTICS_AGGREGATION_HOUR: int = 2  # Run at 2 AM
    
    # Embedding Model
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
