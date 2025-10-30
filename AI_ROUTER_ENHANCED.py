"""
AI Router Enhanced - Multi-Model Intelligent Routing

Includes: Ollama, GPT-5, Claude Reasoning, Perplexity, ZhipuAI, GPT-OSS
Optimized for cost, quality, and compliance (China + Global)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List, Dict
import tiktoken
import logging

logger = logging.getLogger(__name__)


class ModelProvider(Enum):
    """Available AI model providers"""
    OLLAMA_LLAMA = "ollama:llama3.1"
    OLLAMA_LLAMA_70B = "ollama:llama3.1:70b"
    OLLAMA_QWEN = "ollama:qwen2.5"
    GPT5 = "openai:gpt-5"
    GPT4O = "openai:gpt-4o"
    GPT4O_MINI = "openai:gpt-4o-mini"
    CLAUDE_SONNET = "anthropic:claude-sonnet-4"
    CLAUDE_REASONING = "anthropic:claude-reasoning"
    PERPLEXITY = "perplexity:sonar-pro"
    ZHIPU_GLM4 = "zhipu:glm-4"
    ZHIPU_GLM4_FLASH = "zhipu:glm-4-flash"
    DEEPSEEK_R1 = "deepseek:deepseek-r1"
    GPT_OSS = "oss:gpt-oss"


class TaskType(Enum):
    """Types of tasks the AI can perform"""
    WEB_SEARCH = "web_search"
    COMPLEX_REASONING = "complex_reasoning"
    CODE_GENERATION = "code_generation"
    FAQ = "faq"
    SIMPLE_CHAT = "simple_chat"
    SENTIMENT_ANALYSIS = "sentiment"
    EMAIL_DRAFT = "email_draft"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    CHINESE_NLP = "chinese_nlp"
    COST_SENSITIVE = "cost_sensitive"
    CREATIVE = "creative"


@dataclass
class RoutingDecision:
    """Result of the routing decision"""
    provider: ModelProvider
    confidence: float
    reasoning: str
    estimated_cost: float
    task_type: TaskType
    latency_estimate_ms: int
    region: str  # global, china, both


class EnhancedIntelligentRouter:
    """
    Enhanced AI Model Router with China + Global support
    
    Core innovation: Routes queries to optimal model based on:
    - Task complexity
    - User tier (free/starter/pro/enterprise)
    - Cost vs quality tradeoff
    - Latency requirements
    - Regional requirements (China compliance)
    - Model capabilities
    """
    
    def __init__(self, user_tier: str, conversation_context: dict = None, region: str = "global"):
        self.user_tier = user_tier
        self.context = conversation_context or {}
        self.region = region
        self.tokenizer = tiktoken.encoding_for_model("gpt-4")
        
        # Tier to allowed models mapping
        self.tier_models = {
            "free": [
                ModelProvider.OLLAMA_LLAMA,
                ModelProvider.OLLAMA_QWEN,
                ModelProvider.OLLAMA_LLAMA_70B,
                ModelProvider.ZHIPU_GLM4_FLASH,  # Free tier for testing
            ],
            "starter": [
                ModelProvider.OLLAMA_LLAMA,
                ModelProvider.OLLAMA_QWEN,
                ModelProvider.GPT4O_MINI,
                ModelProvider.ZHIPU_GLM4_FLASH,
            ],
            "pro": [
                ModelProvider.OLLAMA_LLAMA,
                ModelProvider.OLLAMA_QWEN,
                ModelProvider.GPT4O_MINI,
                ModelProvider.GPT4O,
                ModelProvider.CLAUDE_SONNET,
                ModelProvider.PERPLEXITY,
                ModelProvider.ZHIPU_GLM4,
                ModelProvider.ZHIPU_GLM4_FLASH,
            ],
            "enterprise": list(ModelProvider)  # All models
        }
        
        # Cost per 1K tokens (USD)
        self.model_costs = {
            ModelProvider.OLLAMA_LLAMA: 0.0,
            ModelProvider.OLLAMA_LLAMA_70B: 0.0,
            ModelProvider.OLLAMA_QWEN: 0.0,
            ModelProvider.GPT4O_MINI: 0.00015,
            ModelProvider.GPT4O: 0.005,
            ModelProvider.GPT5: 0.03,
            ModelProvider.CLAUDE_SONNET: 0.003,
            ModelProvider.CLAUDE_REASONING: 0.01,
            ModelProvider.PERPLEXITY: 0.001,
            ModelProvider.ZHIPU_GLM4: 0.001,
            ModelProvider.ZHIPU_GLM4_FLASH: 0.0005,
            ModelProvider.DEEPSEEK_R1: 0.0005,
            ModelProvider.GPT_OSS: 0.0001
        }
        
        # Latency estimates (milliseconds)
        self.model_latency = {
            ModelProvider.OLLAMA_LLAMA: 500,
            ModelProvider.OLLAMA_LLAMA_70B: 2000,
            ModelProvider.OLLAMA_QWEN: 600,
            ModelProvider.GPT4O_MINI: 800,
            ModelProvider.GPT4O: 1200,
            ModelProvider.GPT5: 1500,
            ModelProvider.CLAUDE_SONNET: 1000,
            ModelProvider.CLAUDE_REASONING: 2000,
            ModelProvider.PERPLEXITY: 3000,
            ModelProvider.ZHIPU_GLM4: 900,
            ModelProvider.ZHIPU_GLM4_FLASH: 500,
            ModelProvider.DEEPSEEK_R1: 1500,
            ModelProvider.GPT_OSS: 1000
        }
    
    def route(self, user_message: str, task_type: Optional[TaskType] = None, priority: str = "quality") -> RoutingDecision:
        """
        Main routing logic - selects optimal model
        
        Args:
            user_message: The user's input message
            task_type: Optional pre-classified task type
            priority: "quality", "cost", "speed", or "balanced"
            
        Returns:
            RoutingDecision with selected model and metadata
        """
        logger.info(f"Routing message for tier: {self.user_tier}, region: {self.region}")
        
        # Calculate token count
        tokens = len(self.tokenizer.encode(user_message))
        
        # Classify task if not provided
        if not task_type:
            task_type = self._classify_task(user_message)
        
        logger.info(f"Classified task: {task_type.value}, tokens: {tokens}, priority: {priority}")
        
        # Regional routing for China compliance
        if self.region == "china" or self._is_chinese_content(user_message):
            return self._route_for_china(tokens, task_type, priority)
        
        # Standard routing
        if task_type == TaskType.WEB_SEARCH:
            return self._route_web_search(tokens, priority)
        elif task_type == TaskType.COMPLEX_REASONING:
            return self._route_complex_reasoning(tokens, priority)
        elif task_type == TaskType.CODE_GENERATION:
            return self._route_code_generation(tokens, priority)
        elif task_type == TaskType.CHINESE_NLP:
            return self._route_chinese_nlp(tokens)
        elif task_type in [TaskType.FAQ, TaskType.SIMPLE_CHAT, TaskType.SENTIMENT_ANALYSIS]:
            return self._route_simple_task(tokens, task_type)
        elif task_type == TaskType.EMAIL_DRAFT:
            return self._route_email_draft(tokens)
        elif task_type == TaskType.TRANSLATION:
            return self._route_translation(tokens)
        elif task_type == TaskType.SUMMARIZATION:
            return self._route_summarization(tokens, priority)
        elif task_type == TaskType.COST_SENSITIVE:
            return self._route_cost_sensitive(tokens)
        else:
            # Default balanced routing
            return self._route_default(tokens, task_type, priority)
    
    def _is_chinese_content(self, message: str) -> bool:
        """Detect if content is in Chinese"""
        chinese_chars = sum(1 for char in message if '\u4e00' <= char <= '\u9fff')
        return chinese_chars > len(message) * 0.1  # 10% Chinese characters
    
    def _classify_task(self, message: str) -> TaskType:
        """
        Enhanced task classification using keyword matching
        """
        message_lower = message.lower()
        
        # Chinese content
        if self._is_chinese_content(message):
            return TaskType.CHINESE_NLP
        
        # Web search indicators
        web_indicators = ["latest", "current", "today", "news", "search", "find", "what is happening", "recent"]
        if any(indicator in message_lower for indicator in web_indicators):
            return TaskType.WEB_SEARCH
        
        # Code generation indicators
        code_indicators = ["code", "function", "script", "program", "implement", "algorithm", "debug"]
        if any(indicator in message_lower for indicator in code_indicators):
            return TaskType.CODE_GENERATION
        
        # Complex reasoning indicators
        complex_indicators = ["analyze", "explain why", "compare", "evaluate", "strategy", "plan", "reasoning"]
        if any(indicator in message_lower for indicator in complex_indicators):
            return TaskType.COMPLEX_REASONING
        
        # Email draft indicators
        email_indicators = ["email", "draft", "write to", "reply to", "compose"]
        if any(indicator in message_lower for indicator in email_indicators):
            return TaskType.EMAIL_DRAFT
        
        # Translation indicators
        if "translate" in message_lower or "translation" in message_lower:
            return TaskType.TRANSLATION
        
        # Summarization indicators
        if "summarize" in message_lower or "summary" in message_lower or "tldr" in message_lower:
            return TaskType.SUMMARIZATION
        
        # Cost sensitive indicators
        cost_indicators = ["free", "cheap", "budget", "low cost", "cost effective"]
        if any(indicator in message_lower for indicator in cost_indicators):
            return TaskType.COST_SENSITIVE
        
        # FAQ indicators (short questions)
        if len(message.split()) < 10 and "?" in message:
            return TaskType.FAQ
        
        # Default to simple chat
        return TaskType.SIMPLE_CHAT
    
    def _route_for_china(self, tokens: int, task_type: TaskType, priority: str) -> RoutingDecision:
        """Route queries for China region (compliance)"""
        
        # China routing: prefer ZhipuAI or local Ollama
        if self.user_tier in ["pro", "enterprise"]:
            if ModelProvider.ZHIPU_GLM4 in self.tier_models[self.user_tier]:
                return RoutingDecision(
                    provider=ModelProvider.ZHIPU_GLM4,
                    confidence=0.95,
                    reasoning="China region: Using ZhipuAI for compliance",
                    estimated_cost=self.model_costs[ModelProvider.ZHIPU_GLM4] * (tokens / 1000),
                    task_type=task_type,
                    latency_estimate_ms=self.model_latency[ModelProvider.ZHIPU_GLM4],
                    region="china"
                )
        else:
            # Free/Starter: use Ollama Qwen (Chinese optimized)
            return RoutingDecision(
                provider=ModelProvider.OLLAMA_QWEN,
                confidence=0.90,
                reasoning="China region: Using local Qwen for zero cost",
                estimated_cost=0.0,
                task_type=task_type,
                latency_estimate_ms=self.model_latency[ModelProvider.OLLAMA_QWEN],
                region="china"
            )
    
    def _route_web_search(self, tokens: int, priority: str) -> RoutingDecision:
        """Route queries requiring web search"""
        if ModelProvider.PERPLEXITY in self.tier_models[self.user_tier]:
            return RoutingDecision(
                provider=ModelProvider.PERPLEXITY,
                confidence=0.95,
                reasoning="Real-time web search required - using Perplexity",
                estimated_cost=self.model_costs[ModelProvider.PERPLEXITY] * (tokens / 1000),
                task_type=TaskType.WEB_SEARCH,
                latency_estimate_ms=self.model_latency[ModelProvider.PERPLEXITY],
                region="global"
            )
        else:
            # Fallback for lower tiers
            return RoutingDecision(
                provider=ModelProvider.OLLAMA_LLAMA,
                confidence=0.60,
                reasoning="Web search unavailable in current tier - using knowledge cutoff",
                estimated_cost=0.0,
                task_type=TaskType.WEB_SEARCH,
                latency_estimate_ms=self.model_latency[ModelProvider.OLLAMA_LLAMA],
                region="global"
            )
    
    def _route_complex_reasoning(self, tokens: int, priority: str) -> RoutingDecision:
        """Route complex analytical tasks"""
        
        if priority == "quality":
            if self.user_tier in ["pro", "enterprise"]:
                if ModelProvider.CLAUDE_REASONING in self.tier_models[self.user_tier]:
                    return RoutingDecision(
                        provider=ModelProvider.CLAUDE_REASONING,
                        confidence=0.92,
                        reasoning="Complex reasoning: Using Claude Reasoning model",
                        estimated_cost=self.model_costs[ModelProvider.CLAUDE_REASONING] * (tokens / 1000),
                        task_type=TaskType.COMPLEX_REASONING,
                        latency_estimate_ms=self.model_latency[ModelProvider.CLAUDE_REASONING],
                        region="global"
                    )
                elif ModelProvider.GPT5 in self.tier_models[self.user_tier]:
                    return RoutingDecision(
                        provider=ModelProvider.GPT5,
                        confidence=0.90,
                        reasoning="Complex reasoning: Using GPT-5",
                        estimated_cost=self.model_costs[ModelProvider.GPT5] * (tokens / 1000),
                        task_type=TaskType.COMPLEX_REASONING,
                        latency_estimate_ms=self.model_latency[ModelProvider.GPT5],
                        region="global"
                    )
        
        elif priority == "cost":
            return RoutingDecision(
                provider=ModelProvider.DEEPSEEK_R1,
                confidence=0.85,
                reasoning="Cost-optimized reasoning: Using DeepSeek-R1",
                estimated_cost=self.model_costs[ModelProvider.DEEPSEEK_R1] * (tokens / 1000),
                task_type=TaskType.COMPLEX_REASONING,
                latency_estimate_ms=self.model_latency[ModelProvider.DEEPSEEK_R1],
                region="global"
            )
        
        elif priority == "speed":
            return RoutingDecision(
                provider=ModelProvider.GPT4O_MINI,
                confidence=0.80,
                reasoning="Fast reasoning: Using GPT-4o-mini",
                estimated_cost=self.model_costs[ModelProvider.GPT4O_MINI] * (tokens / 1000),
                task_type=TaskType.COMPLEX_REASONING,
                latency_estimate_ms=self.model_latency[ModelProvider.GPT4O_MINI],
                region="global"
            )
        
        # Balanced: use Ollama for small, Claude for large
        if tokens < 2000:
            return RoutingDecision(
                provider=ModelProvider.OLLAMA_LLAMA_70B,
                confidence=0.75,
                reasoning="Balanced: Local 70B model for cost efficiency",
                estimated_cost=0.0,
                task_type=TaskType.COMPLEX_REASONING,
                latency_estimate_ms=self.model_latency[ModelProvider.OLLAMA_LLAMA_70B],
                region="global"
            )
        else:
            return RoutingDecision(
                provider=ModelProvider.CLAUDE_SONNET,
                confidence=0.85,
                reasoning="Balanced: Claude for complex multi-step reasoning",
                estimated_cost=self.model_costs[ModelProvider.CLAUDE_SONNET] * (tokens / 1000),
                task_type=TaskType.COMPLEX_REASONING,
                latency_estimate_ms=self.model_latency[ModelProvider.CLAUDE_SONNET],
                region="global"
            )
    
    def _route_code_generation(self, tokens: int, priority: str) -> RoutingDecision:
        """Route code generation tasks"""
        if tokens > 4000 or self.user_tier == "enterprise":
            return RoutingDecision(
                provider=ModelProvider.GPT5,
                confidence=0.92,
                reasoning="Large codebase: Using GPT-5 for best quality",
                estimated_cost=self.model_costs[ModelProvider.GPT5] * (tokens / 1000),
                task_type=TaskType.CODE_GENERATION,
                latency_estimate_ms=self.model_latency[ModelProvider.GPT5],
                region="global"
            )
        else:
            # Use local model for cost efficiency
            return RoutingDecision(
                provider=ModelProvider.OLLAMA_QWEN,
                confidence=0.85,
                reasoning="Code generation: Using Qwen2.5-Coder (free)",
                estimated_cost=0.0,
                task_type=TaskType.CODE_GENERATION,
                latency_estimate_ms=self.model_latency[ModelProvider.OLLAMA_QWEN],
                region="global"
            )
    
    def _route_chinese_nlp(self, tokens: int) -> RoutingDecision:
        """Route Chinese NLP tasks"""
        if ModelProvider.ZHIPU_GLM4 in self.tier_models[self.user_tier]:
            return RoutingDecision(
                provider=ModelProvider.ZHIPU_GLM4,
                confidence=0.95,
                reasoning="Chinese content: Using ZhipuAI GLM-4 (optimized)",
                estimated_cost=self.model_costs[ModelProvider.ZHIPU_GLM4] * (tokens / 1000),
                task_type=TaskType.CHINESE_NLP,
                latency_estimate_ms=self.model_latency[ModelProvider.ZHIPU_GLM4],
                region="china"
            )
        else:
            # Fallback to Qwen (Chinese-optimized local model)
            return RoutingDecision(
                provider=ModelProvider.OLLAMA_QWEN,
                confidence=0.85,
                reasoning="Chinese content: Using local Qwen (zero cost)",
                estimated_cost=0.0,
                task_type=TaskType.CHINESE_NLP,
                latency_estimate_ms=self.model_latency[ModelProvider.OLLAMA_QWEN],
                region="global"
            )
    
    def _route_simple_task(self, tokens: int, task_type: TaskType) -> RoutingDecision:
        """Route simple tasks (FAQ, chat, sentiment)"""
        return RoutingDecision(
            provider=ModelProvider.OLLAMA_LLAMA,
            confidence=0.88,
            reasoning="Simple task: Handled locally with zero API cost",
            estimated_cost=0.0,
            task_type=task_type,
            latency_estimate_ms=self.model_latency[ModelProvider.OLLAMA_LLAMA],
            region="global"
        )
    
    def _route_cost_sensitive(self, tokens: int) -> RoutingDecision:
        """Route cost-sensitive tasks"""
        return RoutingDecision(
            provider=ModelProvider.OLLAMA_LLAMA,
            confidence=0.90,
            reasoning="Cost-sensitive: Using free local model",
            estimated_cost=0.0,
            task_type=TaskType.COST_SENSITIVE,
            latency_estimate_ms=self.model_latency[ModelProvider.OLLAMA_LLAMA],
            region="global"
        )
    
    def _route_email_draft(self, tokens: int) -> RoutingDecision:
        """Route email drafting tasks"""
        if self.user_tier in ["pro", "enterprise"]:
            return RoutingDecision(
                provider=ModelProvider.CLAUDE_SONNET,
                confidence=0.90,
                reasoning="Professional email drafting: Using Claude",
                estimated_cost=self.model_costs[ModelProvider.CLAUDE_SONNET] * (tokens / 1000),
                task_type=TaskType.EMAIL_DRAFT,
                latency_estimate_ms=self.model_latency[ModelProvider.CLAUDE_SONNET],
                region="global"
            )
        else:
            return RoutingDecision(
                provider=ModelProvider.OLLAMA_LLAMA,
                confidence=0.75,
                reasoning="Email drafting: Using local model",
                estimated_cost=0.0,
                task_type=TaskType.EMAIL_DRAFT,
                latency_estimate_ms=self.model_latency[ModelProvider.OLLAMA_LLAMA],
                region="global"
            )
    
    def _route_translation(self, tokens: int) -> RoutingDecision:
        """Route translation tasks"""
        return RoutingDecision(
            provider=ModelProvider.OLLAMA_LLAMA,
            confidence=0.85,
            reasoning="Translation: Handled efficiently by local model",
            estimated_cost=0.0,
            task_type=TaskType.TRANSLATION,
            latency_estimate_ms=self.model_latency[ModelProvider.OLLAMA_LLAMA],
            region="global"
        )
    
    def _route_summarization(self, tokens: int, priority: str) -> RoutingDecision:
        """Route summarization tasks"""
        if tokens > 8000:
            # Large documents
            if self.user_tier in ["pro", "enterprise"]:
                return RoutingDecision(
                    provider=ModelProvider.CLAUDE_SONNET,
                    confidence=0.90,
                    reasoning="Long document: Using Claude for quality",
                    estimated_cost=self.model_costs[ModelProvider.CLAUDE_SONNET] * (tokens / 1000),
                    task_type=TaskType.SUMMARIZATION,
                    latency_estimate_ms=self.model_latency[ModelProvider.CLAUDE_SONNET],
                    region="global"
                )
            else:
                return RoutingDecision(
                    provider=ModelProvider.GPT4O_MINI,
                    confidence=0.80,
                    reasoning="Long document: Using GPT-4o-mini (cost-effective)",
                    estimated_cost=self.model_costs[ModelProvider.GPT4O_MINI] * (tokens / 1000),
                    task_type=TaskType.SUMMARIZATION,
                    latency_estimate_ms=self.model_latency[ModelProvider.GPT4O_MINI],
                    region="global"
                )
        else:
            return RoutingDecision(
                provider=ModelProvider.OLLAMA_LLAMA,
                confidence=0.85,
                reasoning="Standard summarization: Local model (free)",
                estimated_cost=0.0,
                task_type=TaskType.SUMMARIZATION,
                latency_estimate_ms=self.model_latency[ModelProvider.OLLAMA_LLAMA],
                region="global"
            )
    
    def _route_default(self, tokens: int, task_type: TaskType, priority: str) -> RoutingDecision:
        """Default balanced routing"""
        
        if priority == "quality":
            if self.user_tier in ["pro", "enterprise"]:
                return RoutingDecision(
                    provider=ModelProvider.GPT4O,
                    confidence=0.80,
                    reasoning="Balanced quality: Using GPT-4o",
                    estimated_cost=self.model_costs[ModelProvider.GPT4O] * (tokens / 1000),
                    task_type=task_type,
                    latency_estimate_ms=self.model_latency[ModelProvider.GPT4O],
                    region="global"
                )
            else:
                return RoutingDecision(
                    provider=ModelProvider.GPT4O_MINI,
                    confidence=0.75,
                    reasoning="Balanced quality: Using GPT-4o-mini",
                    estimated_cost=self.model_costs[ModelProvider.GPT4O_MINI] * (tokens / 1000),
                    task_type=task_type,
                    latency_estimate_ms=self.model_latency[ModelProvider.GPT4O_MINI],
                    region="global"
                )
        elif priority == "cost":
            return RoutingDecision(
                provider=ModelProvider.OLLAMA_LLAMA,
                confidence=0.75,
                reasoning="Cost optimization: Using free local model",
                estimated_cost=0.0,
                task_type=task_type,
                latency_estimate_ms=self.model_latency[ModelProvider.OLLAMA_LLAMA],
                region="global"
            )
        else:  # balanced or speed
            return RoutingDecision(
                provider=ModelProvider.ZHIPU_GLM4_FLASH,
                confidence=0.80,
                reasoning="Balanced: Fast and cheap with ZhipuAI Flash",
                estimated_cost=self.model_costs[ModelProvider.ZHIPU_GLM4_FLASH] * (tokens / 1000),
                task_type=task_type,
                latency_estimate_ms=self.model_latency[ModelProvider.ZHIPU_GLM4_FLASH],
                region="global"
            )

