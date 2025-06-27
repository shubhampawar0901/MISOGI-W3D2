"""OpenAI provider implementation."""

import time
from typing import List, Dict, Any
import openai
from .base import BaseProvider, ModelResponse, ModelInfo


class OpenAIProvider(BaseProvider):
    """OpenAI API provider for model comparison."""
    
    def __init__(self, api_key: str, config: Dict[str, Any] = None):
        """Initialize OpenAI provider."""
        super().__init__(api_key, config)
        self.client = openai.OpenAI(api_key=api_key)
        self.provider_name = "openai"
    
    def get_available_models(self) -> List[ModelInfo]:
        """Get list of available OpenAI models."""
        models = []
        
        # Define available models based on configuration
        model_configs = self.config.get('providers', {}).get('openai', {})
        
        for model_type in ['base_models', 'instruct_models', 'fine_tuned_models']:
            type_name = model_type.replace('_models', '').replace('_', '_')
            model_list = model_configs.get(model_type, [])
            
            for model_config in model_list:
                if model_config.get('available', False):
                    models.append(ModelInfo(
                        name=model_config['name'],
                        description=model_config['description'],
                        model_type=type_name,
                        context_window=model_config['context_window'],
                        available=model_config['available'],
                        provider=self.provider_name
                    ))
        
        return models
    
    def generate_response(
        self,
        query: str,
        model_name: str,
        model_type: str,
        **kwargs
    ) -> ModelResponse:
        """Generate response using OpenAI API."""
        start_time = time.time()
        
        # Get default settings
        defaults = self.config.get('defaults', {})
        max_tokens = kwargs.get('max_tokens', defaults.get('max_tokens', 1000))
        temperature = kwargs.get('temperature', defaults.get('temperature', 0.7))
        
        try:
            if model_type == 'base':
                # For base models, use completion API (if available)
                response = self.client.completions.create(
                    model=model_name,
                    prompt=query,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                content = response.choices[0].text.strip()
                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens
                
            else:
                # For instruct and fine-tuned models, use chat API
                messages = [{"role": "user", "content": query}]
                
                response = self.client.chat.completions.create(
                    model=model_name,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                content = response.choices[0].message.content
                prompt_tokens = response.usage.prompt_tokens
                completion_tokens = response.usage.completion_tokens
            
            return self._create_response(
                content=content,
                model_name=model_name,
                model_type=model_type,
                start_time=start_time,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                prompt=query,
                finish_reason=response.choices[0].finish_reason,
                model_version=response.model
            )
            
        except Exception as e:
            # Return error response
            return self._create_response(
                content=f"Error: {str(e)}",
                model_name=model_name,
                model_type=model_type,
                start_time=start_time,
                prompt_tokens=0,
                completion_tokens=0,
                prompt=query,
                error=str(e)
            )
    
    def validate_api_key(self) -> bool:
        """Validate OpenAI API key."""
        try:
            # Try to list models as a simple validation
            self.client.models.list()
            return True
        except Exception:
            return False
