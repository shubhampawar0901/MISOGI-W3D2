"""
Multimodal QA Web App Backend
FastAPI server for handling image uploads and multimodal question answering.
"""

import os
import base64
import requests
from io import BytesIO
from typing import Optional, Dict, Any
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from PIL import Image
import logging
from dotenv import load_dotenv
from config import config
from model_service import model_service

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Multimodal QA API", version="1.0.0")

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration is now handled by config.py and model_service.py

class QuestionRequest(BaseModel):
    question: str
    image_url: Optional[str] = None
    use_fallback: bool = False

class AnalysisResponse(BaseModel):
    answer: str
    model_used: str
    processing_time: float
    confidence: Optional[float] = None
    fallback_used: bool = False
    error: Optional[str] = None

def encode_image_to_base64(image_data: bytes) -> str:
    """Convert image bytes to base64 string."""
    return base64.b64encode(image_data).decode('utf-8')

def validate_image(image_data: bytes) -> bool:
    """Validate if the uploaded data is a valid image."""
    try:
        image = Image.open(BytesIO(image_data))
        # Check if it's a valid image format
        image.verify()

        # Check file size
        if len(image_data) > config.get_max_file_size_bytes():
            return False

        return True
    except Exception as e:
        logger.error(f"Image validation failed: {e}")
        return False

def download_image_from_url(url: str) -> bytes:
    """Download image from URL and return bytes."""
    try:
        response = requests.get(url, timeout=config.api.request_timeout)
        response.raise_for_status()

        # Validate content type
        content_type = response.headers.get('content-type', '')
        if not config.is_image_type_allowed(content_type):
            raise ValueError(f"URL does not point to a valid image. Content-Type: {content_type}")

        # Check file size
        if len(response.content) > config.get_max_file_size_bytes():
            raise ValueError(f"Image file too large. Maximum size: {config.api.max_file_size_mb}MB")

        return response.content
    except Exception as e:
        logger.error(f"Failed to download image from URL: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to download image: {str(e)}")

@app.get("/")
async def root():
    """Health check endpoint."""
    return {"message": "Multimodal QA API is running", "status": "healthy"}

@app.get("/status")
async def get_status():
    """Get API and model status."""
    return model_service.get_model_status()

@app.post("/upload", response_model=AnalysisResponse)
async def upload_and_analyze(
    file: UploadFile = File(...),
    question: str = Form(...)
):
    """Upload an image and analyze it with a question."""
    try:
        # Read and validate image
        image_data = await file.read()
        if not validate_image(image_data):
            raise HTTPException(status_code=400, detail="Invalid image format or file too large")

        # Convert to base64
        image_base64 = encode_image_to_base64(image_data)

        # Analyze using model service
        result = await model_service.analyze_image(question, image_base64)

        return AnalysisResponse(
            answer=result["answer"],
            model_used=result["model_used"],
            processing_time=result["processing_time"],
            fallback_used=result.get("fallback_used", False)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/analyze-url", response_model=AnalysisResponse)
async def analyze_image_url(request: QuestionRequest):
    """Analyze an image from URL with a question."""
    if not request.image_url:
        raise HTTPException(status_code=400, detail="Image URL is required")

    try:
        # Download image from URL
        image_data = download_image_from_url(request.image_url)

        # Validate image
        if not validate_image(image_data):
            raise HTTPException(status_code=400, detail="URL does not point to a valid image or file too large")

        # Convert to base64
        image_base64 = encode_image_to_base64(image_data)

        # Analyze using model service
        result = await model_service.analyze_image(request.question, image_base64)

        return AnalysisResponse(
            answer=result["answer"],
            model_used=result["model_used"],
            processing_time=result["processing_time"],
            fallback_used=result.get("fallback_used", False)
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"URL analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
