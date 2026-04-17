"""
Video Dublagem Automática - Main Application
Automatic video dubbing system with AI
"""

import logging
import os
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('app.log')
    ]
)

logger = logging.getLogger(__name__)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Dict, Any
from datetime import datetime

# Import configuration
from app.config.settings import (
    DEBUG, HOST, PORT, BASE_DIR, 
    INPUT_DIR, AUDIO_DIR, OUTPUT_DIR
)

# Import routes
from app.routes.process import router as process_router


# Create FastAPI app
app = FastAPI(
    title="Video Dublagem Automática",
    description="Sistema de dublagem automática de vídeos com IA",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if DEBUG else "An error occurred"
        }
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    logger.info("=" * 60)
    logger.info("Video Dublagem Automática - Iniciando")
    logger.info("=" * 60)
    
    # Verify required directories
    for directory in [INPUT_DIR, AUDIO_DIR, OUTPUT_DIR]:
        directory.mkdir(parents=True, exist_ok=True)
        logger.info(f"Directory ready: {directory}")
    
    # Log configuration
    logger.info(f"Base directory: {BASE_DIR}")
    logger.info(f"Debug mode: {DEBUG}")
    logger.info(f"Server: {HOST}:{PORT}")
    
    # Check for required tools
    try:
        import subprocess
        
        tools = ['ffmpeg', 'ffprobe', 'yt-dlp']
        for tool in tools:
            result = subprocess.run(
                [tool, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.info(f"✓ {tool} is available")
            else:
                logger.warning(f"⚠ {tool} might not be properly installed")
    except Exception as e:
        logger.error(f"Error checking tools: {str(e)}")
    
    logger.info("Application started successfully")


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    logger.info("=" * 60)
    logger.info("Video Dublagem Automática - Encerrando")
    logger.info("=" * 60)


# Root endpoint
@app.get("/")
async def root() -> Dict[str, Any]:
    """
    Root endpoint with API information
    
    Returns:
        API information
    """
    return {
        "name": "Video Dublagem Automática",
        "version": "1.0.0",
        "description": "Sistema de dublagem automática de vídeos com IA",
        "endpoints": {
            "POST /api/processar": "Processar e dublar vídeo",
            "GET /api/status": "Status do processamento",
            "GET /api/health": "Health check",
            "GET /docs": "Documentação interativa (Swagger)",
            "GET /redoc": "Documentação (ReDoc)"
        },
        "timestamp": datetime.now().isoformat()
    }


# Include routers
app.include_router(process_router)


# Detailed documentation endpoint
@app.get("/info")
async def get_info() -> Dict[str, Any]:
    """
    Get detailed application information
    
    Returns:
        Detailed info
    """
    return {
        "application": "Video Dublagem Automática",
        "version": "1.0.0",
        "description": "Sistema completo de dublagem automática de vídeos usando IA",
        "features": [
            "Download automático de vídeos",
            "Extração de áudio com FFmpeg",
            "Transcrição com OpenAI Whisper",
            "Tradução com GPT para português",
            "Otimização para dublagem natural",
            "Geração de áudio com TTS da OpenAI",
            "Sincronização de áudio com vídeo",
            "Upload automático para YouTube"
        ],
        "storage_info": {
            "input_directory": str(INPUT_DIR),
            "audio_directory": str(AUDIO_DIR),
            "output_directory": str(OUTPUT_DIR)
        },
        "api_version": "1.0",
        "timestamp": datetime.now().isoformat()
    }


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting Uvicorn server on {HOST}:{PORT}")
    
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=DEBUG,
        log_level="info"
    )
