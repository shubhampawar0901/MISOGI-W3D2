"""Configuration management for the model comparison tool."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv


class Config:
    """Configuration manager for the model comparison tool."""
    
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize configuration from file and environment variables."""
        self.config_path = Path(config_path)
        self._config = {}
        self._load_config()
        self._load_env_vars()
    
    def _load_config(self):
        """Load configuration from YAML file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self._config = yaml.safe_load(f)
        else:
            # Default configuration if file doesn't exist
            self._config = {
                'providers': {},
                'defaults': {
                    'max_tokens': 1000,
                    'temperature': 0.7
                },
                'visualization': {
                    'enabled': True,
                    'save_plots': False
                }
            }
    
    def _load_env_vars(self):
        """Load environment variables from .env file."""
        # Look for .env file in the same directory as config
        env_path = self.config_path.parent / '.env'
        if env_path.exists():
            load_dotenv(env_path)
        else:
            # Try loading from current directory
            load_dotenv()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a specific provider."""
        env_var_map = {
            'openai': 'OPENAI_API_KEY',
            'anthropic': 'ANTHROPIC_API_KEY',
            'huggingface': 'HUGGINGFACE_API_KEY'
        }
        
        env_var = env_var_map.get(provider.lower())
        if env_var:
            return os.getenv(env_var)
        return None
    
    def get_models(self, provider: str, model_type: str = None) -> Dict[str, Any]:
        """Get models for a specific provider and type."""
        provider_config = self.get(f'providers.{provider}', {})
        
        if model_type:
            return provider_config.get(f'{model_type}_models', [])
        
        # Return all models for the provider
        all_models = {}
        for mtype in ['base', 'instruct', 'fine_tuned']:
            models = provider_config.get(f'{mtype}_models', [])
            all_models[mtype] = models
        
        return all_models
    
    def get_available_models(self, provider: str, model_type: str = None) -> Dict[str, Any]:
        """Get only available models for a specific provider and type."""
        models = self.get_models(provider, model_type)
        
        if model_type:
            return [model for model in models if model.get('available', False)]
        
        # Filter available models for all types
        available_models = {}
        for mtype, model_list in models.items():
            available_models[mtype] = [
                model for model in model_list if model.get('available', False)
            ]
        
        return available_models
    
    def get_default_settings(self) -> Dict[str, Any]:
        """Get default model settings."""
        return self.get('defaults', {})
    
    def is_visualization_enabled(self) -> bool:
        """Check if visualization is enabled."""
        return self.get('visualization.enabled', True)
    
    def should_save_plots(self) -> bool:
        """Check if plots should be saved."""
        return self.get('visualization.save_plots', False)
    
    def get_plot_output_dir(self) -> str:
        """Get plot output directory."""
        return self.get('visualization.output_directory', './plots')
    
    def validate_api_keys(self) -> Dict[str, bool]:
        """Validate that required API keys are present."""
        providers = ['openai', 'anthropic', 'huggingface']
        validation_results = {}
        
        for provider in providers:
            api_key = self.get_api_key(provider)
            validation_results[provider] = api_key is not None and len(api_key.strip()) > 0
        
        return validation_results
