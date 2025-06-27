"""Model manager for coordinating multiple providers and models."""

import asyncio
import concurrent.futures
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from config import Config
from providers.base import ModelResponse, ModelInfo
from providers.openai_provider import OpenAIProvider
from providers.anthropic_provider import AnthropicProvider
from providers.huggingface_provider import HuggingFaceProvider


@dataclass
class ComparisonResult:
    """Result of a model comparison."""
    query: str
    responses: List[ModelResponse]
    summary: Dict[str, Any]


class ModelManager:
    """Manages multiple model providers and coordinates comparisons."""
    
    def __init__(self, config: Config):
        """Initialize model manager with configuration."""
        self.config = config
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all available providers."""
        provider_classes = {
            'openai': OpenAIProvider,
            'anthropic': AnthropicProvider,
            'huggingface': HuggingFaceProvider
        }
        
        for provider_name, provider_class in provider_classes.items():
            api_key = self.config.get_api_key(provider_name)
            if api_key:
                try:
                    self.providers[provider_name] = provider_class(
                        api_key=api_key,
                        config=self.config._config
                    )
                except Exception as e:
                    print(f"Warning: Failed to initialize {provider_name} provider: {e}")
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return list(self.providers.keys())
    
    def get_available_models(self, provider: str = None) -> List[ModelInfo]:
        """Get available models from specified provider or all providers."""
        models = []
        
        if provider and provider in self.providers:
            models.extend(self.providers[provider].get_available_models())
        elif provider == "all" or provider is None:
            for provider_instance in self.providers.values():
                models.extend(provider_instance.get_available_models())
        
        return models
    
    def get_models_by_type(self, model_type: str, provider: str = None) -> List[ModelInfo]:
        """Get models filtered by type."""
        all_models = self.get_available_models(provider)
        return [model for model in all_models if model.model_type == model_type]
    
    def compare_models(
        self,
        query: str,
        model_type: str = "all",
        provider: str = "all",
        max_concurrent: int = 3,
        **kwargs
    ) -> List[ModelResponse]:
        """Compare models across providers and types."""
        # Determine which models to use
        target_models = self._select_models_for_comparison(model_type, provider)
        
        if not target_models:
            return []
        
        # Generate responses concurrently
        responses = self._generate_responses_concurrent(
            query, target_models, max_concurrent, **kwargs
        )
        
        return responses
    
    def _select_models_for_comparison(
        self,
        model_type: str,
        provider: str
    ) -> List[tuple]:
        """Select models for comparison based on criteria."""
        selected_models = []
        
        # Determine target providers
        target_providers = []
        if provider == "all":
            target_providers = list(self.providers.keys())
        elif provider in self.providers:
            target_providers = [provider]
        
        # Determine target model types
        target_types = []
        if model_type == "all":
            target_types = ["base", "instruct", "fine_tuned"]
        else:
            target_types = [model_type]
        
        # Select models
        for provider_name in target_providers:
            provider_instance = self.providers[provider_name]
            
            for mtype in target_types:
                models = provider_instance.get_models_by_type(mtype)
                for model in models:
                    if model.available:
                        selected_models.append((provider_name, model.name, model.model_type))
        
        return selected_models
    
    def _generate_responses_concurrent(
        self,
        query: str,
        target_models: List[tuple],
        max_concurrent: int,
        **kwargs
    ) -> List[ModelResponse]:
        """Generate responses from multiple models concurrently."""
        responses = []
        
        # Use ThreadPoolExecutor for concurrent API calls
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_concurrent) as executor:
            # Submit all tasks
            future_to_model = {}
            for provider_name, model_name, model_type in target_models:
                future = executor.submit(
                    self._generate_single_response,
                    provider_name, model_name, model_type, query, **kwargs
                )
                future_to_model[future] = (provider_name, model_name, model_type)
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_model):
                try:
                    response = future.result(timeout=60)  # 60 second timeout
                    if response:
                        responses.append(response)
                except Exception as e:
                    provider_name, model_name, model_type = future_to_model[future]
                    print(f"Error with {provider_name}/{model_name}: {e}")
        
        return responses
    
    def _generate_single_response(
        self,
        provider_name: str,
        model_name: str,
        model_type: str,
        query: str,
        **kwargs
    ) -> Optional[ModelResponse]:
        """Generate a single response from a specific model."""
        try:
            provider = self.providers[provider_name]
            response = provider.generate_response(
                query=query,
                model_name=model_name,
                model_type=model_type,
                **kwargs
            )
            return response
        except Exception as e:
            print(f"Error generating response from {provider_name}/{model_name}: {e}")
            return None
    
    def create_comparison_summary(self, responses: List[ModelResponse]) -> Dict[str, Any]:
        """Create a summary of the comparison results."""
        if not responses:
            return {}
        
        summary = {
            "total_responses": len(responses),
            "providers_used": list(set(r.provider for r in responses)),
            "model_types_used": list(set(r.model_type for r in responses)),
            "average_response_time": sum(r.response_time for r in responses) / len(responses),
            "total_tokens_used": sum(r.token_usage["total_tokens"] for r in responses),
            "fastest_response": min(responses, key=lambda r: r.response_time),
            "slowest_response": max(responses, key=lambda r: r.response_time),
            "most_tokens": max(responses, key=lambda r: r.token_usage["total_tokens"]),
            "least_tokens": min(responses, key=lambda r: r.token_usage["total_tokens"])
        }
        
        # Add provider-specific statistics
        provider_stats = {}
        for provider in summary["providers_used"]:
            provider_responses = [r for r in responses if r.provider == provider]
            provider_stats[provider] = {
                "count": len(provider_responses),
                "avg_response_time": sum(r.response_time for r in provider_responses) / len(provider_responses),
                "total_tokens": sum(r.token_usage["total_tokens"] for r in provider_responses)
            }
        
        summary["provider_stats"] = provider_stats
        
        return summary
    
    def validate_providers(self) -> Dict[str, bool]:
        """Validate all initialized providers."""
        validation_results = {}
        
        for provider_name, provider in self.providers.items():
            try:
                validation_results[provider_name] = provider.validate_api_key()
            except Exception:
                validation_results[provider_name] = False
        
        return validation_results
