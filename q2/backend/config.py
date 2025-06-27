"""
Configuration settings for the Multimodal QA backend.
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass

@dataclass
class ModelConfig:
    """Configuration for a specific model."""
    name: str
    provider: str
    supports_vision: bool
    max_tokens: int
    temperature: float
    priority: int  # Lower number = higher priority

@dataclass
class APIConfig:
    """API configuration settings."""
    openai_api_key: str
    anthropic_api_key: str
    google_api_key: str
    max_file_size_mb: int
    allowed_image_types: List[str]
    request_timeout: int

class Config:
    """Main configuration class."""
    
    def __init__(self):
        self.api = APIConfig(
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY", ""),
            google_api_key=os.getenv("GOOGLE_API_KEY", ""),
            max_file_size_mb=int(os.getenv("MAX_FILE_SIZE_MB", "10")),
            allowed_image_types=[
                "image/jpeg", "image/jpg", "image/png", 
                "image/gif", "image/bmp", "image/webp"
            ],
            request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30"))
        )
        
        self.models = [
            ModelConfig(
                name="gpt-4o",
                provider="openai",
                supports_vision=True,
                max_tokens=1000,
                temperature=0.7,
                priority=1
            ),
            ModelConfig(
                name="claude-3-sonnet-20240229",
                provider="anthropic",
                supports_vision=True,
                max_tokens=1000,
                temperature=0.7,
                priority=2
            ),
            ModelConfig(
                name="gpt-3.5-turbo",
                provider="openai",
                supports_vision=False,
                max_tokens=500,
                temperature=0.7,
                priority=3
            )
        ]
    
    def get_available_vision_models(self) -> List[ModelConfig]:
        """Get list of available vision models sorted by priority."""
        vision_models = [m for m in self.models if m.supports_vision]
        
        # Filter by available API keys
        available_models = []
        for model in vision_models:
            if model.provider == "openai" and self.api.openai_api_key:
                available_models.append(model)
            elif model.provider == "anthropic" and self.api.anthropic_api_key:
                available_models.append(model)
            elif model.provider == "google" and self.api.google_api_key:
                available_models.append(model)
        
        return sorted(available_models, key=lambda x: x.priority)
    
    def get_fallback_models(self) -> List[ModelConfig]:
        """Get list of available fallback (text-only) models."""
        fallback_models = [m for m in self.models if not m.supports_vision]
        
        # Filter by available API keys
        available_models = []
        for model in fallback_models:
            if model.provider == "openai" and self.api.openai_api_key:
                available_models.append(model)
            elif model.provider == "anthropic" and self.api.anthropic_api_key:
                available_models.append(model)
        
        return sorted(available_models, key=lambda x: x.priority)
    
    def is_image_type_allowed(self, content_type: str) -> bool:
        """Check if the image content type is allowed."""
        return content_type.lower() in self.api.allowed_image_types
    
    def get_max_file_size_bytes(self) -> int:
        """Get maximum file size in bytes."""
        return self.api.max_file_size_mb * 1024 * 1024

# Global configuration instance
config = Config()
