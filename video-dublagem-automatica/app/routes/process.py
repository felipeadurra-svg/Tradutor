import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

from app.services.downloader import VideoDownloader, DownloadError
from app.services.transcription import TranscriptionService, TranscriptionError
from app.services.translation import TranslationService, TranslationError
from app.services.tts import TTSService, TTSError
from app.services.video_processing import VideoProcessor, VideoProcessingError
from app.services.youtube_uploader import YouTubeUploader, YouTubeError
from app.config.settings import STORAGE_DIR


# Request models
class ProcessVideoRequest(BaseModel):
    """Request model for video processing"""
    video_url: str = Field(..., description="URL of the video to process")
    titulo: str = Field(..., description="Title for the dubbed video")
    descricao: str = Field(default="", description="Description for YouTube")
    privacidade: str = Field(default="public", description="Video privacy (public, private, unlisted)")
    tags: list = Field(default_factory=list, description="Tags for YouTube")
    velocidade_fala: float = Field(default=1.0, description="Speech speed (0.25 to 4.0)")
    voz_tts: str = Field(default="nova", description="TTS voice")


class ProcessVideoResponse(BaseModel):
    """Response model for video processing"""
    success: bool
    message: str
    video_id: Optional[str] = None
    youtube_url: Optional[str] = None
    local_file_path: Optional[str] = None
    local_file_url: Optional[str] = None
    duration: Optional[float] = None
    transcription: Optional[str] = None
    status: str


class ProcessingStatusResponse(BaseModel):
    """Response model for processing status"""
    status: str
    message: str
    progress: int  # 0-100
    current_step: str


class ProcessingResultResponse(BaseModel):
    """Response model for the latest processing result"""
    result: Optional[ProcessVideoResponse] = None


# Initialize router
router = APIRouter(prefix="/api", tags=["processing"])

# Global state for tracking processing
processing_state = {
    "status": "idle",
    "progress": 0,
    "current_step": "",
    "message": ""
}

latest_result: Optional[Dict[str, Any]] = None


async def _update_state(status: str, progress: int, step: str, message: str = ""):
    """Update global processing state"""
    processing_state["status"] = status
    processing_state["progress"] = progress
    processing_state["current_step"] = step
    processing_state["message"] = message
    logger.info(f"State: {step} ({progress}%) - {message}")


def _set_state(status: str, progress: int, step: str, message: str = "") -> None:
    """Synchronous state update for long-running synchronous callbacks."""
    processing_state["status"] = status
    processing_state["progress"] = progress
    processing_state["current_step"] = step
    processing_state["message"] = message
    logger.info(f"State: {step} ({progress}%) - {message}")


def _progress_within_range(
    completed: int,
    total: int,
    start_progress: int,
    end_progress: int
) -> int:
    """Map sub-step progress into the global pipeline range."""
    if total <= 0:
        return start_progress

    ratio = max(0.0, min(1.0, completed / total))
    return start_progress + int((end_progress - start_progress) * ratio)


def _store_latest_result(result: Dict[str, Any]) -> None:
    """Store the latest processing result for UI consumption."""
    global latest_result
    latest_result = result


def _build_media_url(file_path: str) -> str:
    """Build a browser-friendly URL for generated files inside storage."""
    relative_path = Path(file_path).resolve().relative_to(STORAGE_DIR.resolve())
    return f"/media/{relative_path.as_posix()}"


async def _process_video_task(
    video_url: str,
    titulo: str,
    descricao: str,
    privacidade: str,
    tags: list,
    velocidade_fala: float,
    voz_tts: str
) -> Dict[str, Any]:
    """
    Background task to process video
    
    Args:
        video_url: URL of video to process
        titulo: Video title
        descricao: Video description
        privacidade: Privacy setting
        tags: Video tags
        velocidade_fala: Speech speed
        voz_tts: TTS voice
        
    Returns:
        Dictionary with processing results
    """
    try:
        global latest_result
        latest_result = None

        logger.info(f"Starting video processing for URL: {video_url}")
        await _update_state("processing", 5, "Downloading video", "Iniciando download")
        
        # Step 1: Download video
        downloader = VideoDownloader()
        download_result = downloader.download_video(video_url)
        video_path = download_result["file_path"]
        
        logger.info(f"Video downloaded: {video_path}")
        await _update_state("processing", 15, "Extracting audio", "Extraindo áudio do vídeo")
        
        # Step 2: Extract audio
        processor = VideoProcessor()
        audio_path = processor.extract_audio_from_video(video_path)
        
        logger.info(f"Audio extracted: {audio_path}")
        await _update_state("processing", 20, "Transcribing audio", "Transcrevendo áudio")
        
        # Step 3: Transcribe
        transcription_service = TranscriptionService()

        def transcription_progress(completed: int, total: int) -> None:
            progress = _progress_within_range(completed, total, 20, 45)
            _set_state(
                "processing",
                progress,
                "Transcribing audio",
                f"Transcrevendo audio: parte {min(completed, total)}/{total}" if total > 1 else "Transcrevendo áudio"
            )

        transcription_result = transcription_service.transcribe_audio(
            audio_path,
            progress_callback=transcription_progress
        )
        segments = transcription_result["segments"]
        original_text = transcription_result["text"]
        
        logger.info(f"Transcription completed: {len(original_text)} characters")
        await _update_state("processing", 45, "Translating text", "Traduzindo para português")
        
        # Step 4: Translate segments
        translation_service = TranslationService()

        def translation_progress(completed: int, total: int) -> None:
            progress = _progress_within_range(completed, total, 45, 65)
            _set_state(
                "processing",
                progress,
                "Translating text",
                f"Traduzindo trechos: {completed}/{total}"
            )

        translated_segments = translation_service.translate_segments(
            segments,
            source_language="English",
            target_language="Brazilian Portuguese",
            progress_callback=translation_progress
        )
        
        # Optimize for dubbing
        optimized_segments = translation_service.optimize_for_dubbing(translated_segments)
        
        logger.info(f"Translation completed: {len(optimized_segments)} segments")
        await _update_state("processing", 65, "Generating TTS audio", "Gerando áudio em português")
        
        # Step 5: Generate TTS
        tts_service = TTSService()

        def tts_progress(completed: int, total: int) -> None:
            progress = _progress_within_range(completed, total, 65, 85)
            _set_state(
                "processing",
                progress,
                "Generating TTS audio",
                f"Gerando voz: {completed}/{total}"
            )

        tts_result = tts_service.generate_segments_audio(
            optimized_segments,
            voice=voz_tts,
            speed=velocidade_fala,
            progress_callback=tts_progress
        )
        
        segments_with_audio = tts_result["segments"]
        
        logger.info(f"TTS generation completed: {tts_result['successful']} segments")
        await _update_state("processing", 85, "Processing video", "Processando vídeo final")
        
        # Step 6: Create dubbed video
        dubbed_video_path = processor.process_video_pipeline(
            video_path,
            segments_with_audio
        )
        
        logger.info(f"Dubbed video created: {dubbed_video_path}")
        await _update_state("processing", 95, "Uploading to YouTube", "Enviando para YouTube")
        
        # Step 7: Upload to YouTube
        try:
            uploader = YouTubeUploader()
            upload_result = uploader.upload_video(
                dubbed_video_path,
                title=titulo,
                description=descricao,
                tags=tags,
                privacy_status=privacidade
            )
            
            youtube_url = upload_result["url"]
            video_id = upload_result["video_id"]
            
            logger.info(f"Video uploaded to YouTube: {youtube_url}")
            await _update_state("processing", 100, "Complete", "Processamento concluído")
            
            result = {
                "success": True,
                "message": "Vídeo dublado e enviado para YouTube com sucesso!",
                "video_id": video_id,
                "youtube_url": youtube_url,
                "local_file_path": dubbed_video_path,
                "local_file_url": _build_media_url(dubbed_video_path),
                "transcription": original_text,
                "status": "completed"
            }
            _store_latest_result(result)
            return result
            
        except YouTubeError as e:
            logger.warning(f"YouTube upload failed, but local file ready: {str(e)}")
            await _update_state("processing", 100, "Complete (No Upload)", "Vídeo pronto localmente")
            
            result = {
                "success": True,
                "message": f"Vídeo dublado criado, mas upload ao YouTube falhou: {str(e)}",
                "video_id": None,
                "youtube_url": None,
                "local_file_path": dubbed_video_path,
                "local_file_url": _build_media_url(dubbed_video_path),
                "transcription": original_text,
                "status": "completed_local_only"
            }
            _store_latest_result(result)
            return result
        
    except DownloadError as e:
        logger.error(f"Download error: {str(e)}")
        await _update_state("error", 0, "Download failed", str(e))
        result = {
            "success": False,
            "message": f"Erro ao baixar vídeo: {str(e)}",
            "status": "error"
        }
        _store_latest_result(result)
        return result
    
    except TranscriptionError as e:
        logger.error(f"Transcription error: {str(e)}")
        await _update_state("error", 0, "Transcription failed", str(e))
        result = {
            "success": False,
            "message": f"Erro na transcrição: {str(e)}",
            "status": "error"
        }
        _store_latest_result(result)
        return result
    
    except TranslationError as e:
        logger.error(f"Translation error: {str(e)}")
        await _update_state("error", 0, "Translation failed", str(e))
        result = {
            "success": False,
            "message": f"Erro na tradução: {str(e)}",
            "status": "error"
        }
        _store_latest_result(result)
        return result
    
    except TTSError as e:
        logger.error(f"TTS error: {str(e)}")
        await _update_state("error", 0, "TTS failed", str(e))
        result = {
            "success": False,
            "message": f"Erro na geração de áudio: {str(e)}",
            "status": "error"
        }
        _store_latest_result(result)
        return result
    
    except VideoProcessingError as e:
        logger.error(f"Video processing error: {str(e)}")
        await _update_state("error", 0, "Video processing failed", str(e))
        result = {
            "success": False,
            "message": f"Erro no processamento de vídeo: {str(e)}",
            "status": "error"
        }
        _store_latest_result(result)
        return result
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        await _update_state("error", 0, "Unexpected error", str(e))
        result = {
            "success": False,
            "message": f"Erro inesperado: {str(e)}",
            "status": "error"
        }
        _store_latest_result(result)
        return result


@router.post("/processar", response_model=ProcessVideoResponse)
async def processar_video(
    request: ProcessVideoRequest,
    background_tasks: BackgroundTasks
) -> ProcessVideoResponse:
    """
    Main endpoint to process and dub a video
    
    Args:
        request: ProcessVideoRequest with video URL and options
        background_tasks: FastAPI background tasks
        
    Returns:
        ProcessVideoResponse with results
    """
    try:
        logger.info(f"Received video processing request for: {request.video_url}")
        
        # Validate URL
        if not request.video_url or not request.video_url.startswith(('http://', 'https://')):
            raise HTTPException(
                status_code=400,
                detail="URL de vídeo inválida"
            )
        
        # Validate privacy setting
        if request.privacidade not in ['public', 'private', 'unlisted']:
            raise HTTPException(
                status_code=400,
                detail="Privacidade deve ser 'public', 'private' ou 'unlisted'"
            )
        
        # Validate speech speed
        if not (0.25 <= request.velocidade_fala <= 4.0):
            raise HTTPException(
                status_code=400,
                detail="Velocidade de fala deve estar entre 0.25 e 4.0"
            )
        
        await _update_state("queued", 0, "Queued", "Vídeo recebido e aguardando processamento")

        # Add task to background processing
        background_tasks.add_task(
            _process_video_task,
            request.video_url,
            request.titulo,
            request.descricao,
            request.privacidade,
            request.tags,
            request.velocidade_fala,
            request.voz_tts
        )
        
        logger.info("Video processing task queued")
        
        return ProcessVideoResponse(
            success=True,
            message="Vídeo enfileirado para processamento. Acompanhe o progresso em /status",
            status="queued",
            video_id=None,
            youtube_url=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in /processar endpoint: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar requisição: {str(e)}"
        )


@router.get("/status", response_model=ProcessingStatusResponse)
async def get_processing_status() -> ProcessingStatusResponse:
    """
    Get current processing status
    
    Returns:
        ProcessingStatusResponse with current state
    """
    return ProcessingStatusResponse(
        status=processing_state["status"],
        message=processing_state["message"],
        progress=processing_state["progress"],
        current_step=processing_state["current_step"]
    )


@router.get("/resultado", response_model=ProcessingResultResponse)
async def get_processing_result() -> ProcessingResultResponse:
    """
    Get the latest processing result.

    Returns:
        ProcessingResultResponse with the latest result, when available
    """
    if latest_result is None:
        return ProcessingResultResponse(result=None)

    return ProcessingResultResponse(result=ProcessVideoResponse(**latest_result))


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint
    
    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }
