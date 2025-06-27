"""Base provider interface for model comparison tool."""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import time


@dataclass
class ModelResponse:
    """Standardized response from a model."""
    content: str
    model_name: str
    provider: str
    model_type: str
    token_usage: Dict[str, int]
    response_time: float
    context_window: int
    metadata: Dict[str, Any]


@dataclass
class ModelInfo:
    """Information about a model."""
    name: str
    description: str
    model_type: str  # base, instruct, fine_tuned
    context_window: int
    available: bool
    provider: str


class BaseProvider(ABC):
    """Abstract base class for model providers."""
    
    def __init__(self, api_key: str, config: Dict[str, Any] = None):
        """Initialize the provider with API key and configuration."""
        self.api_key = api_key
        self.config = config or {}
        self.provider_name = self.__class__.__name__.lower().replace('provider', '')
    
    @abstractmethod
    def get_available_models(self) -> List[ModelInfo]:
        """Get list of available models from this provider."""
        pass
    
    @abstractmethod
    def generate_response(
        self,
        query: str,
        model_name: str,
        model_type: str,
        **kwargs
    ) -> ModelResponse:
        """Generate response from the specified model."""
        pass
    
    def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Get information about a specific model."""
        models = self.get_available_models()
        for model in models:
            if model.name == model_name:
                return model
        return None
    
    def get_models_by_type(self, model_type: str) -> List[ModelInfo]:
        """Get models filtered by type."""
        models = self.get_available_models()
        return [model for model in models if model.model_type == model_type]
    
    def validate_api_key(self) -> bool:
        """Validate that the API key is working."""
        try:
            # Try to get available models as a simple validation
            self.get_available_models()
            return True
        except Exception:
            return False
    
    def _calculate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)."""
        # Simple approximation: ~4 characters per token
        return len(text) // 4
    
    def _create_response(
        self,
        content: str,
        model_name: str,
        model_type: str,
        start_time: float,
        prompt_tokens: int = None,
        completion_tokens: int = None,
        **metadata
    ) -> ModelResponse:
        """Create a standardized ModelResponse object."""
        response_time = time.time() - start_time
        
        # Get model info for context window
        model_info = self.get_model_info(model_name)
        context_window = model_info.context_window if model_info else 0
        
        # Calculate token usage if not provided
        if prompt_tokens is None:
            prompt_tokens = self._calculate_tokens(metadata.get('prompt', ''))
        if completion_tokens is None:
            completion_tokens = self._calculate_tokens(content)
        
        token_usage = {
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': prompt_tokens + completion_tokens
        }
        
        return ModelResponse(
            content=content,
            model_name=model_name,
            provider=self.provider_name,
            model_type=model_type,
            token_usage=token_usage,
            response_time=response_time,
            context_window=context_window,
            metadata=metadata
        )
