"""Hugging Face provider implementation."""

import time
from typing import List, Dict, Any
import requests
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from .base import BaseProvider, ModelResponse, ModelInfo


class HuggingFaceProvider(BaseProvider):
    """Hugging Face provider for model comparison."""
    
    def __init__(self, api_key: str, config: Dict[str, Any] = None):
        """Initialize Hugging Face provider."""
        super().__init__(api_key, config)
        self.provider_name = "huggingface"
        self.api_url = "https://api-inference.huggingface.co/models"
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self._loaded_models = {}  # Cache for locally loaded models
    
    def get_available_models(self) -> List[ModelInfo]:
        """Get list of available Hugging Face models."""
        models = []
        
        # Define available models based on configuration
        model_configs = self.config.get('providers', {}).get('huggingface', {})
        
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
    
    def _query_api(self, model_name: str, query: str, **kwargs) -> str:
        """Query Hugging Face Inference API."""
        url = f"{self.api_url}/{model_name}"
        
        payload = {
            "inputs": query,
            "parameters": {
                "max_new_tokens": kwargs.get('max_tokens', 1000),
                "temperature": kwargs.get('temperature', 0.7),
                "return_full_text": False
            }
        }
        
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        if isinstance(result, list) and len(result) > 0:
            return result[0].get('generated_text', '')
        return str(result)
    
    def _load_model_locally(self, model_name: str):
        """Load model locally using transformers."""
        if model_name not in self._loaded_models:
            try:
                tokenizer = AutoTokenizer.from_pretrained(model_name)
                model = AutoModelForCausalLM.from_pretrained(
                    model_name,
                    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
                    device_map="auto" if torch.cuda.is_available() else None
                )
                self._loaded_models[model_name] = {
                    'tokenizer': tokenizer,
                    'model': model
                }
            except Exception as e:
                raise Exception(f"Failed to load model {model_name}: {str(e)}")
        
        return self._loaded_models[model_name]
    
    def _generate_locally(self, model_name: str, query: str, **kwargs) -> str:
        """Generate response using locally loaded model."""
        model_components = self._load_model_locally(model_name)
        tokenizer = model_components['tokenizer']
        model = model_components['model']
        
        # Tokenize input
        inputs = tokenizer.encode(query, return_tensors="pt")
        
        # Generate response
        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_new_tokens=kwargs.get('max_tokens', 1000),
                temperature=kwargs.get('temperature', 0.7),
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id
            )
        
        # Decode response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Remove the input prompt from the response
        if response.startswith(query):
            response = response[len(query):].strip()
        
        return response
    
    def generate_response(
        self,
        query: str,
        model_name: str,
        model_type: str,
        use_local: bool = False,
        **kwargs
    ) -> ModelResponse:
        """Generate response using Hugging Face model."""
        start_time = time.time()
        
        try:
            if use_local:
                content = self._generate_locally(model_name, query, **kwargs)
            else:
                content = self._query_api(model_name, query, **kwargs)
            
            # Calculate token usage
            prompt_tokens = self._calculate_tokens(query)
            completion_tokens = self._calculate_tokens(content)
            
            return self._create_response(
                content=content,
                model_name=model_name,
                model_type=model_type,
                start_time=start_time,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                prompt=query,
                method="local" if use_local else "api",
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
        """Validate Hugging Face API key."""
        try:
            # Try to query a simple model
            test_url = f"{self.api_url}/gpt2"
            response = requests.post(
                test_url,
                headers=self.headers,
                json={"inputs": "Hello"}
            )
            return response.status_code == 200
        except Exception:
            return False
