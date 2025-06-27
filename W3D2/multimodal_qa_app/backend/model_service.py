"""
Model service for handling multimodal AI requests with fallback support.
"""

import time
import logging
from typing import Dict, Any, Optional, List
import openai
import anthropic
from config import config, ModelConfig

logger = logging.getLogger(__name__)

class ModelService:
    """Service for managing multimodal AI model requests."""
    
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        
        # Initialize clients if API keys are available
        if config.api.openai_api_key:
            self.openai_client = openai.OpenAI(api_key=config.api.openai_api_key)
        
        if config.api.anthropic_api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=config.api.anthropic_api_key)
    
    async def analyze_image(self, question: str, image_base64: str) -> Dict[str, Any]:
        """
        Analyze an image with a question using the best available model.
        
        Args:
            question: The question to ask about the image
            image_base64: Base64 encoded image data
            
        Returns:
            Dictionary containing the analysis result
        """
        vision_models = config.get_available_vision_models()
        
        if not vision_models:
            logger.warning("No vision models available, using fallback")
            return await self._fallback_analysis(question)
        
        # Try each vision model in order of priority
        for model in vision_models:
            try:
                logger.info(f"Attempting analysis with {model.name}")
                result = await self._analyze_with_model(model, question, image_base64)
                result["fallback_used"] = False
                return result
            except Exception as e:
                logger.warning(f"Model {model.name} failed: {e}")
                continue
        
        # If all vision models fail, use fallback
        logger.warning("All vision models failed, using fallback")
        result = await self._fallback_analysis(question)
        result["fallback_used"] = True
        return result
    
    async def _analyze_with_model(
        self, 
        model: ModelConfig, 
        question: str, 
        image_base64: str
    ) -> Dict[str, Any]:
        """Analyze image with a specific model."""
        start_time = time.time()
        
        if model.provider == "openai":
            return await self._analyze_with_openai(model, question, image_base64, start_time)
        elif model.provider == "anthropic":
            return await self._analyze_with_anthropic(model, question, image_base64, start_time)
        else:
            raise ValueError(f"Unsupported provider: {model.provider}")
    
    async def _analyze_with_openai(
        self, 
        model: ModelConfig, 
        question: str, 
        image_base64: str, 
        start_time: float
    ) -> Dict[str, Any]:
        """Analyze image using OpenAI GPT-4o."""
        if not self.openai_client:
            raise ValueError("OpenAI client not initialized")
        
        response = self.openai_client.chat.completions.create(
            model=model.name,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ],
            max_tokens=model.max_tokens,
            temperature=model.temperature
        )
        
        processing_time = time.time() - start_time
        
        return {
            "answer": response.choices[0].message.content,
            "model_used": model.name,
            "processing_time": processing_time,
            "tokens_used": response.usage.total_tokens if response.usage else None,
            "provider": model.provider
        }
    
    async def _analyze_with_anthropic(
        self, 
        model: ModelConfig, 
        question: str, 
        image_base64: str, 
        start_time: float
    ) -> Dict[str, Any]:
        """Analyze image using Anthropic Claude."""
        if not self.anthropic_client:
            raise ValueError("Anthropic client not initialized")
        
        response = self.anthropic_client.messages.create(
            model=model.name,
            max_tokens=model.max_tokens,
            temperature=model.temperature,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_base64
                            }
                        },
                        {
                            "type": "text",
                            "text": question
                        }
                    ]
                }
            ]
        )
        
        processing_time = time.time() - start_time
        
        return {
            "answer": response.content[0].text,
            "model_used": model.name,
            "processing_time": processing_time,
            "tokens_used": (
                response.usage.input_tokens + response.usage.output_tokens 
                if response.usage else None
            ),
            "provider": model.provider
        }
    
    async def _fallback_analysis(self, question: str) -> Dict[str, Any]:
        """Perform fallback text-only analysis."""
        start_time = time.time()
        fallback_models = config.get_fallback_models()
        
        if not fallback_models:
            return {
                "answer": "I apologize, but I'm unable to process your request at the moment. Please check your API configuration and try again.",
                "model_used": "system_fallback",
                "processing_time": time.time() - start_time,
                "tokens_used": 0,
                "provider": "system",
                "fallback_used": True
            }
        
        # Try fallback models
        for model in fallback_models:
            try:
                if model.provider == "openai" and self.openai_client:
                    response = self.openai_client.chat.completions.create(
                        model=model.name,
                        messages=[
                            {
                                "role": "user",
                                "content": f"I'm unable to process the image, but here's the question: {question}. Please provide a helpful response acknowledging that you cannot see the image but offering general guidance if possible."
                            }
                        ],
                        max_tokens=model.max_tokens,
                        temperature=model.temperature
                    )
                    
                    return {
                        "answer": response.choices[0].message.content,
                        "model_used": f"{model.name} (fallback)",
                        "processing_time": time.time() - start_time,
                        "tokens_used": response.usage.total_tokens if response.usage else None,
                        "provider": model.provider,
                        "fallback_used": True
                    }
            except Exception as e:
                logger.warning(f"Fallback model {model.name} failed: {e}")
                continue
        
        # Ultimate fallback
        return {
            "answer": "I apologize, but I'm unable to process your image or question at the moment. This could be due to API limitations or configuration issues. Please try again later or contact support.",
            "model_used": "system_fallback",
            "processing_time": time.time() - start_time,
            "tokens_used": 0,
            "provider": "system",
            "fallback_used": True
        }
    
    def get_model_status(self) -> Dict[str, Any]:
        """Get the status of available models."""
        vision_models = config.get_available_vision_models()
        fallback_models = config.get_fallback_models()
        
        return {
            "vision_models_available": len(vision_models),
            "fallback_models_available": len(fallback_models),
            "vision_models": [
                {
                    "name": m.name,
                    "provider": m.provider,
                    "priority": m.priority
                } for m in vision_models
            ],
            "fallback_models": [
                {
                    "name": m.name,
                    "provider": m.provider,
                    "priority": m.priority
                } for m in fallback_models
            ],
            "openai_configured": bool(config.api.openai_api_key),
            "anthropic_configured": bool(config.api.anthropic_api_key),
            "google_configured": bool(config.api.google_api_key)
        }

# Global model service instance
model_service = ModelService()
