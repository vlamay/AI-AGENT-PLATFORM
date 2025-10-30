from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List
import httpx
import openai
import anthropic
import logging

from app.core.config import settings
from app.core.router import ModelProvider

logger = logging.getLogger(__name__)


@dataclass
class ModelResponse:
    """Standardized response from any model"""
    text: str
    model: str
    tokens_used: int
    latency_ms: int
    cost_usd: float


class BaseModelClient(ABC):
    """Abstract base class for all model clients"""
    
    @abstractmethod
    async def generate(
        self,
        prompt: str,
        agent_id: str,
        conversation_id: str,
        context: Optional[List[dict]] = None
    ) -> ModelResponse:
        """Generate response from the model"""
        pass


class OllamaClient(BaseModelClient):
    """Client for local Ollama models"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name.replace("ollama:", "")
        self.endpoint = settings.OLLAMA_ENDPOINT
    
    async def generate(
        self,
        prompt: str,
        agent_id: str,
        conversation_id: str,
        context: Optional[List[dict]] = None
    ) -> ModelResponse:
        """Generate response using Ollama"""
        import time
        start_time = time.time()
        
        # Get RAG context if available
        rag_context = await self._get_rag_context(agent_id, prompt)
        
        # Build full prompt with context
        full_prompt = self._build_prompt(prompt, rag_context, context)
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    f"{self.endpoint}/api/generate",
                    json={
                        "model": self.model_name,
                        "prompt": full_prompt,
                        "stream": False
                    }
                )
                response.raise_for_status()
                
                result = response.json()
                latency_ms = int((time.time() - start_time) * 1000)
                
                return ModelResponse(
                    text=result["response"],
                    model=f"ollama:{self.model_name}",
                    tokens_used=result.get("total_duration", 0),
                    latency_ms=latency_ms,
                    cost_usd=0.0  # Local models are free
                )
                
            except Exception as e:
                logger.error(f"Ollama error: {str(e)}")
                raise
    
    async def _get_rag_context(self, agent_id: str, query: str) -> List[str]:
        """Retrieve relevant context from knowledge base"""
        from app.services.rag_service import RAGService
        
        rag_service = RAGService()
        try:
            results = await rag_service.search(agent_id, query, top_k=3)
            return results
        except:
            return []
    
    def _build_prompt(
        self,
        prompt: str,
        rag_context: List[str],
        conversation_context: Optional[List[dict]]
    ) -> str:
        """Build enhanced prompt with context"""
        parts = []
        
        # Add RAG context
        if rag_context:
            parts.append("# Relevant Knowledge Base:\n")
            for i, ctx in enumerate(rag_context, 1):
                parts.append(f"{i}. {ctx}\n")
            parts.append("\n")
        
        # Add conversation history
        if conversation_context:
            parts.append("# Conversation History:\n")
            for msg in conversation_context[-5:]:  # Last 5 messages
                role = msg.get("role", "user")
                content = msg.get("content", "")
                parts.append(f"{role}: {content}\n")
            parts.append("\n")
        
        # Add current prompt
        parts.append(f"# Current Query:\n{prompt}\n\n")
        parts.append("# Response:")
        
        return "".join(parts)


class OpenAIClient(BaseModelClient):
    """Client for OpenAI models"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name.replace("openai:", "")
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def generate(
        self,
        prompt: str,
        agent_id: str,
        conversation_id: str,
        context: Optional[List[dict]] = None
    ) -> ModelResponse:
        """Generate response using OpenAI"""
        import time
        start_time = time.time()
        
        # Build messages
        messages = [{"role": "system", "content": "You are a helpful AI assistant."}]
        
        if context:
            messages.extend(context[-10:])  # Last 10 messages
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=2000
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Calculate cost
            tokens_used = response.usage.total_tokens
            cost_per_1k = settings.MODEL_COSTS.get(f"openai:{self.model_name}", 0.00015)
            cost_usd = (tokens_used / 1000) * cost_per_1k
            
            return ModelResponse(
                text=response.choices[0].message.content,
                model=f"openai:{self.model_name}",
                tokens_used=tokens_used,
                latency_ms=latency_ms,
                cost_usd=cost_usd
            )
            
        except Exception as e:
            logger.error(f"OpenAI error: {str(e)}")
            raise


class AnthropicClient(BaseModelClient):
    """Client for Anthropic Claude models"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name.replace("anthropic:", "")
        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    
    async def generate(
        self,
        prompt: str,
        agent_id: str,
        conversation_id: str,
        context: Optional[List[dict]] = None
    ) -> ModelResponse:
        """Generate response using Claude"""
        import time
        start_time = time.time()
        
        # Build messages (Claude format)
        messages = []
        if context:
            for msg in context[-10:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        messages.append({"role": "user", "content": prompt})
        
        try:
            response = await self.client.messages.create(
                model=self.model_name,
                max_tokens=2000,
                messages=messages
            )
            
            latency_ms = int((time.time() - start_time) * 1000)
            
            # Calculate cost
            tokens_used = response.usage.input_tokens + response.usage.output_tokens
            cost_per_1k = settings.MODEL_COSTS.get(f"anthropic:{self.model_name}", 0.003)
            cost_usd = (tokens_used / 1000) * cost_per_1k
            
            return ModelResponse(
                text=response.content[0].text,
                model=f"anthropic:{self.model_name}",
                tokens_used=tokens_used,
                latency_ms=latency_ms,
                cost_usd=cost_usd
            )
            
        except Exception as e:
            logger.error(f"Anthropic error: {str(e)}")
            raise


class PerplexityClient(BaseModelClient):
    """Client for Perplexity (web search)"""
    
    def __init__(self, model_name: str):
        self.model_name = model_name.replace("perplexity:", "")
        self.api_key = settings.PERPLEXITY_API_KEY
    
    async def generate(
        self,
        prompt: str,
        agent_id: str,
        conversation_id: str,
        context: Optional[List[dict]] = None
    ) -> ModelResponse:
        """Generate response with web search"""
        import time
        start_time = time.time()
        
        messages = [{"role": "user", "content": prompt}]
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model_name,
                        "messages": messages
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                
                result = response.json()
                latency_ms = int((time.time() - start_time) * 1000)
                
                tokens_used = result.get("usage", {}).get("total_tokens", 0)
                cost_usd = (tokens_used / 1000) * 0.001
                
                return ModelResponse(
                    text=result["choices"][0]["message"]["content"],
                    model=f"perplexity:{self.model_name}",
                    tokens_used=tokens_used,
                    latency_ms=latency_ms,
                    cost_usd=cost_usd
                )
                
            except Exception as e:
                logger.error(f"Perplexity error: {str(e)}")
                raise


class ModelClientFactory:
    """Factory for creating model clients"""
    
    @staticmethod
    def get_client(provider: ModelProvider) -> BaseModelClient:
        """Get appropriate client for the provider"""
        
        if "ollama" in provider.value:
            model_name = provider.value
            return OllamaClient(model_name)
        
        elif "openai" in provider.value:
            model_name = provider.value
            return OpenAIClient(model_name)
        
        elif "anthropic" in provider.value:
            model_name = provider.value
            return AnthropicClient(model_name)
        
        elif "perplexity" in provider.value:
            model_name = provider.value
            return PerplexityClient(model_name)
        
        else:
            # Default to Ollama Llama
            return OllamaClient("llama3.3")
