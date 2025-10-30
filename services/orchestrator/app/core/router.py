from dataclasses import dataclass
from enum import Enum
from typing import Optional
import tiktoken
import logging

logger = logging.getLogger(__name__)


class ModelProvider(Enum):
    """Available AI model providers"""
    OLLAMA_LLAMA = "ollama:llama3.3"
    OLLAMA_MISTRAL = "ollama:mistral"
    OLLAMA_QWEN = "ollama:qwen2.5"
    GPT4O_MINI = "openai:gpt-4o-mini"
    GPT4O = "openai:gpt-4o"
    CLAUDE_SONNET = "anthropic:claude-sonnet-4"
    PERPLEXITY = "perplexity:sonar-pro"
    DEEPSEEK_R1 = "deepseek:deepseek-r1"


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


@dataclass
class RoutingDecision:
    """Result of the routing decision"""
    provider: ModelProvider
    confidence: float
    reasoning: str
    estimated_cost: float
    task_type: TaskType


class IntelligentRouter:
    """
    Intelligent AI Model Router
    
    Core innovation: Routes queries to optimal model based on:
    - Task complexity
    - User tier (free/starter/pro/enterprise)
    - Cost vs quality tradeoff
    - Latency requirements
    - Model capabilities
    """
    
    def __init__(self, user_tier: str, conversation_context: dict = None):
        self.user_tier = user_tier
        self.context = conversation_context or {}
        self.tokenizer = tiktoken.encoding_for_model("gpt-4")
        
        # Tier to allowed models mapping
        self.tier_models = {
            "free": [
                ModelProvider.OLLAMA_LLAMA,
                ModelProvider.OLLAMA_MISTRAL,
                ModelProvider.OLLAMA_QWEN
            ],
            "starter": [
                ModelProvider.OLLAMA_LLAMA,
                ModelProvider.OLLAMA_MISTRAL,
                ModelProvider.OLLAMA_QWEN,
                ModelProvider.GPT4O_MINI
            ],
            "pro": [
                ModelProvider.OLLAMA_LLAMA,
                ModelProvider.OLLAMA_MISTRAL,
                ModelProvider.OLLAMA_QWEN,
                ModelProvider.GPT4O_MINI,
                ModelProvider.GPT4O,
                ModelProvider.CLAUDE_SONNET,
                ModelProvider.PERPLEXITY
            ],
            "enterprise": list(ModelProvider)  # All models
        }
        
        # Cost per 1K tokens
        self.model_costs = {
            ModelProvider.OLLAMA_LLAMA: 0.0,
            ModelProvider.OLLAMA_MISTRAL: 0.0,
            ModelProvider.OLLAMA_QWEN: 0.0,
            ModelProvider.GPT4O_MINI: 0.00015,
            ModelProvider.GPT4O: 0.005,
            ModelProvider.CLAUDE_SONNET: 0.003,
            ModelProvider.PERPLEXITY: 0.001,
            ModelProvider.DEEPSEEK_R1: 0.0005
        }
    
    def route(self, user_message: str, task_type: Optional[TaskType] = None) -> RoutingDecision:
        """
        Main routing logic - selects optimal model
        
        Args:
            user_message: The user's input message
            task_type: Optional pre-classified task type
            
        Returns:
            RoutingDecision with selected model and metadata
        """
        logger.info(f"Routing message for tier: {self.user_tier}")
        
        # Calculate token count
        tokens = len(self.tokenizer.encode(user_message))
        
        # Classify task if not provided
        if not task_type:
            task_type = self._classify_task(user_message)
        
        logger.info(f"Classified task: {task_type.value}, tokens: {tokens}")
        
        # Route based on task type and user tier
        if task_type == TaskType.WEB_SEARCH:
            return self._route_web_search(tokens)
        
        elif task_type == TaskType.COMPLEX_REASONING:
            return self._route_complex_reasoning(tokens)
        
        elif task_type == TaskType.CODE_GENERATION:
            return self._route_code_generation(tokens)
        
        elif task_type in [TaskType.FAQ, TaskType.SIMPLE_CHAT, TaskType.SENTIMENT_ANALYSIS]:
            return self._route_simple_task(tokens, task_type)
        
        elif task_type == TaskType.EMAIL_DRAFT:
            return self._route_email_draft(tokens)
        
        elif task_type == TaskType.TRANSLATION:
            return self._route_translation(tokens)
        
        elif task_type == TaskType.SUMMARIZATION:
            return self._route_summarization(tokens)
        
        else:
            # Default balanced routing
            return self._route_default(tokens, task_type)
    
    def _classify_task(self, message: str) -> TaskType:
        """
        Lightweight task classification using keyword matching
        Falls back to Ollama for complex cases
        """
        message_lower = message.lower()
        
        # Web search indicators
        web_indicators = ["latest", "current", "today", "news", "search", "find", "what is happening", "recent"]
        if any(indicator in message_lower for indicator in web_indicators):
            return TaskType.WEB_SEARCH
        
        # Code generation indicators
        code_indicators = ["code", "function", "script", "program", "implement", "algorithm", "debug"]
        if any(indicator in message_lower for indicator in code_indicators):
            return TaskType.CODE_GENERATION
        
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
        
        # Complex reasoning indicators
        complex_indicators = ["analyze", "explain why", "compare", "evaluate", "strategy", "plan"]
        if any(indicator in message_lower for indicator in complex_indicators):
            return TaskType.COMPLEX_REASONING
        
        # FAQ indicators (short questions)
        if len(message.split()) < 10 and "?" in message:
            return TaskType.FAQ
        
        # Default to simple chat
        return TaskType.SIMPLE_CHAT
    
    def _route_web_search(self, tokens: int) -> RoutingDecision:
        """Route queries requiring web search"""
        if ModelProvider.PERPLEXITY in self.tier_models[self.user_tier]:
            return RoutingDecision(
                provider=ModelProvider.PERPLEXITY,
                confidence=0.95,
                reasoning="Real-time web search required - using Perplexity",
                estimated_cost=self.model_costs[ModelProvider.PERPLEXITY] * (tokens / 1000),
                task_type=TaskType.WEB_SEARCH
            )
        else:
            # Fallback for lower tiers
            return RoutingDecision(
                provider=ModelProvider.OLLAMA_LLAMA,
                confidence=0.60,
                reasoning="Web search unavailable in current tier - using knowledge cutoff",
                estimated_cost=0.0,
                task_type=TaskType.WEB_SEARCH
            )
    
    def _route_complex_reasoning(self, tokens: int) -> RoutingDecision:
        """Route complex analytical tasks"""
        if self.user_tier in ["pro", "enterprise"]:
            if ModelProvider.CLAUDE_SONNET in self.tier_models[self.user_tier]:
                return RoutingDecision(
                    provider=ModelProvider.CLAUDE_SONNET,
                    confidence=0.92,
                    reasoning="Complex analysis requires advanced reasoning - using Claude Sonnet",
                    estimated_cost=self.model_costs[ModelProvider.CLAUDE_SONNET] * (tokens / 1000),
                    task_type=TaskType.COMPLEX_REASONING
                )
            else:
                return RoutingDecision(
                    provider=ModelProvider.GPT4O,
                    confidence=0.90,
                    reasoning="Complex task requiring GPT-4o capabilities",
                    estimated_cost=self.model_costs[ModelProvider.GPT4O] * (tokens / 1000),
                    task_type=TaskType.COMPLEX_REASONING
                )
        elif self.user_tier == "starter":
            return RoutingDecision(
                provider=ModelProvider.GPT4O_MINI,
                confidence=0.75,
                reasoning="Using GPT-4o-mini for cost-effective reasoning",
                estimated_cost=self.model_costs[ModelProvider.GPT4O_MINI] * (tokens / 1000),
                task_type=TaskType.COMPLEX_REASONING
            )
        else:
            # Free tier
            return RoutingDecision(
                provider=ModelProvider.OLLAMA_LLAMA,
                confidence=0.70,
                reasoning="Free tier: using local Llama 3.3 for reasoning",
                estimated_cost=0.0,
                task_type=TaskType.COMPLEX_REASONING
            )
    
    def _route_code_generation(self, tokens: int) -> RoutingDecision:
        """Route code generation tasks"""
        if tokens > 4000 or self.user_tier == "enterprise":
            return RoutingDecision(
                provider=ModelProvider.GPT4O,
                confidence=0.92,
                reasoning="Large codebase requires GPT-4o",
                estimated_cost=self.model_costs[ModelProvider.GPT4O] * (tokens / 1000),
                task_type=TaskType.CODE_GENERATION
            )
        else:
            # Use specialized code model
            return RoutingDecision(
                provider=ModelProvider.OLLAMA_QWEN,
                confidence=0.85,
                reasoning="Using Qwen2.5-Coder for efficient code generation",
                estimated_cost=0.0,
                task_type=TaskType.CODE_GENERATION
            )
    
    def _route_simple_task(self, tokens: int, task_type: TaskType) -> RoutingDecision:
        """Route simple tasks (FAQ, chat, sentiment)"""
        return RoutingDecision(
            provider=ModelProvider.OLLAMA_LLAMA,
            confidence=0.88,
            reasoning="Simple task handled locally with zero API cost",
            estimated_cost=0.0,
            task_type=task_type
        )
    
    def _route_email_draft(self, tokens: int) -> RoutingDecision:
        """Route email drafting tasks"""
        if self.user_tier in ["pro", "enterprise"]:
            return RoutingDecision(
                provider=ModelProvider.CLAUDE_SONNET,
                confidence=0.90,
                reasoning="Professional email drafting using Claude",
                estimated_cost=self.model_costs[ModelProvider.CLAUDE_SONNET] * (tokens / 1000),
                task_type=TaskType.EMAIL_DRAFT
            )
        else:
            return RoutingDecision(
                provider=ModelProvider.OLLAMA_LLAMA,
                confidence=0.75,
                reasoning="Email drafting with local model",
                estimated_cost=0.0,
                task_type=TaskType.EMAIL_DRAFT
            )
    
    def _route_translation(self, tokens: int) -> RoutingDecision:
        """Route translation tasks"""
        return RoutingDecision(
            provider=ModelProvider.OLLAMA_LLAMA,
            confidence=0.85,
            reasoning="Translation handled efficiently by local model",
            estimated_cost=0.0,
            task_type=TaskType.TRANSLATION
        )
    
    def _route_summarization(self, tokens: int) -> RoutingDecision:
        """Route summarization tasks"""
        if tokens > 8000:
            # Large documents need powerful models
            if self.user_tier in ["pro", "enterprise"]:
                return RoutingDecision(
                    provider=ModelProvider.CLAUDE_SONNET,
                    confidence=0.90,
                    reasoning="Long document summarization using Claude",
                    estimated_cost=self.model_costs[ModelProvider.CLAUDE_SONNET] * (tokens / 1000),
                    task_type=TaskType.SUMMARIZATION
                )
            else:
                return RoutingDecision(
                    provider=ModelProvider.GPT4O_MINI,
                    confidence=0.80,
                    reasoning="Long document with GPT-4o-mini",
                    estimated_cost=self.model_costs[ModelProvider.GPT4O_MINI] * (tokens / 1000),
                    task_type=TaskType.SUMMARIZATION
                )
        else:
            return RoutingDecision(
                provider=ModelProvider.OLLAMA_LLAMA,
                confidence=0.85,
                reasoning="Standard summarization with local model",
                estimated_cost=0.0,
                task_type=TaskType.SUMMARIZATION
            )
    
    def _route_default(self, tokens: int, task_type: TaskType) -> RoutingDecision:
        """Default balanced routing"""
        if self.user_tier in ["pro", "enterprise"]:
            return RoutingDecision(
                provider=ModelProvider.GPT4O_MINI,
                confidence=0.80,
                reasoning="Balanced quality and cost with GPT-4o-mini",
                estimated_cost=self.model_costs[ModelProvider.GPT4O_MINI] * (tokens / 1000),
                task_type=task_type
            )
        else:
            return RoutingDecision(
                provider=ModelProvider.OLLAMA_LLAMA,
                confidence=0.75,
                reasoning="Default local model for cost efficiency",
                estimated_cost=0.0,
                task_type=task_type
            )
