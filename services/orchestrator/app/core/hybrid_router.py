"""
Hybrid Router: LM Studio + Ollama
Automatically routes between LM Studio and Ollama based on availability
"""
import os
import time
import logging
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger(__name__)

class HybridLLMRouter:
    """
    Intelligent router between LM Studio and Ollama
    
    Priority:
    1. Check PREFERRED_LLM env var
    2. Check service availability
    3. Route to available service
    """
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=120.0)
        
        # Endpoints
        self.lm_studio_endpoint = os.getenv("LM_STUDIO_ENDPOINT", "http://localhost:1234")
        self.ollama_endpoint = os.getenv("OLLAMA_ENDPOINT", "http://localhost:11434")
        
        # Preferred LLM (auto, lm_studio, ollama)
        self.preferred = os.getenv("PREFERRED_LLM", "auto")
        
        # Service availability cache
        self._availability_cache = {}
        self._cache_ttl = 60  # seconds
    
    async def route(
        self,
        prompt: str,
        model: Optional[str] = None,
        task_type: str = "chat",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Route request to appropriate LLM service
        """
        
        # Determine which service to use
        endpoint = await self._select_endpoint(model)
        
        logger.info(f"Routing to {endpoint} for task_type={task_type}")
        
        # Call appropriate service
        if "lm_studio" in endpoint or "localhost:1234" in endpoint:
            return await self._call_lm_studio(prompt, model, **kwargs)
        elif "ollama" in endpoint:
            return await self._call_ollama(prompt, model, **kwargs)
        else:
            raise ValueError(f"Unknown endpoint: {endpoint}")
    
    async def _select_endpoint(self, requested_model: Optional[str]) -> str:
        """Select optimal endpoint"""
        
        if self.preferred != "auto":
            # Use explicitly preferred service
            if self.preferred == "lm_studio":
                return self.lm_studio_endpoint
            else:
                return self.ollama_endpoint
        
        # Auto-selection: check availability
        lm_studio_available = await self._check_availability(self.lm_studio_endpoint)
        ollama_available = await self._check_availability(self.ollama_endpoint)
        
        if lm_studio_available and ollama_available:
            # Both available - prefer LM Studio (better UI)
            return self.lm_studio_endpoint
        elif lm_studio_available:
            return self.lm_studio_endpoint
        elif ollama_available:
            return self.ollama_endpoint
        else:
            raise Exception("No local LLM service available (LM Studio or Ollama)")
    
    async def _check_availability(self, endpoint: str) -> bool:
        """Check if service is available"""
        
        # Check cache first
        if endpoint in self._availability_cache:
            cached_result, timestamp = self._availability_cache[endpoint]
            if (time.time() - timestamp) < self._cache_ttl:
                return cached_result
        
        # Check actual availability
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                if "/api/tags" in endpoint or "11434" in endpoint:
                    # Ollama check
                    response = await client.get(f"{self.ollama_endpoint}/api/tags")
                else:
                    # LM Studio check
                    response = await client.get(f"{self.lm_studio_endpoint}/v1/models")
                
                available = response.status_code == 200
                
                # Update cache
                self._availability_cache[endpoint] = (available, time.time())
                
                return available
        except:
            self._availability_cache[endpoint] = (False, time.time())
            return False
    
    async def _call_lm_studio(
        self,
        prompt: str,
        model: Optional[str],
        **kwargs
    ) -> Dict[str, Any]:
        """Call LM Studio API (OpenAI-compatible)"""
        
        url = f"{self.lm_studio_endpoint}/v1/chat/completions"
        
        payload = {
            "model": model or "local-model",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": kwargs.get("temperature", 0.7),
            "max_tokens": kwargs.get("max_tokens", 2000),
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"LM Studio response received")
            
            return {
                "response": data["choices"][0]["message"]["content"],
                "tokens": data.get("usage", {}).get("total_tokens", 0),
                "model": data.get("model", "lm-studio"),
                "provider": "lm_studio",
                "cost": 0.0,  # Always free for local
            }
        except httpx.HTTPError as e:
            logger.error(f"LM Studio API error: {e}")
            # Fallback to Ollama if available
            return await self._call_ollama(prompt, model, **kwargs)
    
    async def _call_ollama(
        self,
        prompt: str,
        model: Optional[str],
        **kwargs
    ) -> Dict[str, Any]:
        """Call Ollama API"""
        
        url = f"{self.ollama_endpoint}/api/generate"
        
        payload = {
            "model": model or "llama3.1:8b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": kwargs.get("temperature", 0.7),
                "num_predict": kwargs.get("max_tokens", 2000),
            }
        }
        
        try:
            response = await self.client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            
            logger.info(f"Ollama response received")
            
            return {
                "response": data.get("response", ""),
                "tokens": data.get("eval_count", 0),
                "model": data.get("model", "ollama"),
                "provider": "ollama",
                "cost": 0.0,  # Always free
            }
        except httpx.HTTPError as e:
            logger.error(f"Ollama API error: {e}")
            raise Exception(f"Both LLM services failed: {e}")
    
    async def list_models(self) -> Dict[str, Any]:
        """List available models from both services"""
        models = {
            "lm_studio": [],
            "ollama": []
        }
        
        # Check LM Studio
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.lm_studio_endpoint}/v1/models")
                if response.status_code == 200:
                    data = response.json()
                    models["lm_studio"] = [m["id"] for m in data.get("data", [])]
        except:
            pass
        
        # Check Ollama
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.ollama_endpoint}/api/tags")
                if response.status_code == 200:
                    data = response.json()
                    models["ollama"] = [m["name"] for m in data.get("models", [])]
        except:
            pass
        
        return models

