"""Anthropic provider implementation."""

import time
from typing import List, Dict, Any
import anthropic
from .base import BaseProvider, ModelResponse, ModelInfo


class AnthropicProvider(BaseProvider):
    """Anthropic API provider for model comparison."""
    
    def __init__(self, api_key: str, config: Dict[str, Any] = None):
        """Initialize Anthropic provider."""
        super().__init__(api_key, config)
        self.client = anthropic.Anthropic(api_key=api_key)
        self.provider_name = "anthropic"
    
    def get_available_models(self) -> List[ModelInfo]:
        """Get list of available Anthropic models."""
        models = []
        
        # Define available models based on configuration
        model_configs = self.config.get('providers', {}).get('anthropic', {})
        
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
        """Generate response using Anthropic API."""
        start_time = time.time()
        
        # Get default settings
        defaults = self.config.get('defaults', {})
        max_tokens = kwargs.get('max_tokens', defaults.get('max_tokens', 1000))
        temperature = kwargs.get('temperature', defaults.get('temperature', 0.7))
        
        try:
            if model_type == 'base':
                # For base models, use completion format
                response = self.client.completions.create(
                    model=model_name,
                    prompt=f"\n\nHuman: {query}\n\nAssistant:",
                    max_tokens_to_sample=max_tokens,
                    temperature=temperature
                )
                content = response.completion.strip()
                
                # Anthropic doesn't provide token usage in the same way
                prompt_tokens = self._calculate_tokens(query)
                completion_tokens = self._calculate_tokens(content)
                
            else:
                # For instruct models, use messages API
                response = self.client.messages.create(
                    model=model_name,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    messages=[
                        {"role": "user", "content": query}
                    ]
                )
                content = response.content[0].text
                
                # Extract token usage if available
                prompt_tokens = getattr(response.usage, 'input_tokens', self._calculate_tokens(query))
                completion_tokens = getattr(response.usage, 'output_tokens', self._calculate_tokens(content))
            
            return self._create_response(
                content=content,
                model_name=model_name,
                model_type=model_type,
                start_time=start_time,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                prompt=query,
                stop_reason=getattr(response, 'stop_reason', 'unknown'),
                model_version=model_name
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
        """Validate Anthropic API key."""
        try:
            # Try a simple completion as validation
            self.client.completions.create(
                model="claude-3-haiku-20240307",
                prompt="\n\nHuman: Hello\n\nAssistant:",
                max_tokens_to_sample=10
            )
            return True
        except Exception:
            return False
