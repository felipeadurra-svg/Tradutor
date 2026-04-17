import logging
from typing import Optional, List, Dict, Any
from openai import OpenAI

logger = logging.getLogger(__name__)

from app.config.settings import OPENAI_API_KEY, WHISPER_MODEL, LANGUAGE_SOURCE


class TranscriptionError(Exception):
    """Raised when transcription fails"""
    pass


class TranscriptionService:
    """Handles audio transcription using OpenAI Whisper"""

    def __init__(self):
        if not OPENAI_API_KEY:
            raise TranscriptionError("OPENAI_API_KEY not configured")
        
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def transcribe_audio(
        self,
        audio_path: str,
        language: str = LANGUAGE_SOURCE
    ) -> Dict[str, Any]:
        """
        Transcribe audio file using Whisper
        
        Args:
            audio_path: Path to audio file
            language: Language code (en, pt, etc)
            
        Returns:
            Dictionary with transcription and metadata
        """
        try:
            logger.info(f"Starting transcription of {audio_path}")
            
            with open(audio_path, "rb") as audio_file:
                transcript = self.client.audio.transcriptions.create(
                    model=WHISPER_MODEL,
                    file=audio_file,
                    language=language,
                    response_format="verbose_json"
                )
            
            logger.info(f"Transcription completed successfully")
            
            # Format response
            result = {
                "text": transcript.text,
                "language": transcript.language if hasattr(transcript, 'language') else language,
                "duration": transcript.duration if hasattr(transcript, 'duration') else 0,
                "segments": self._extract_segments(transcript)
            }
            
            return result
            
        except FileNotFoundError:
            logger.error(f"Audio file not found: {audio_path}")
            raise TranscriptionError(f"Audio file not found: {audio_path}")
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            raise TranscriptionError(f"Failed to transcribe audio: {str(e)}")

    @staticmethod
    def _segment_value(segment: Any, key: str, default: Any = None) -> Any:
        """Read a segment field from either a dict-like or attribute-based SDK object."""
        if isinstance(segment, dict):
            return segment.get(key, default)

        return getattr(segment, key, default)

    @classmethod
    def _extract_segments(transcript) -> List[Dict[str, Any]]:
        """
        Extract segments with timing information
        
        Args:
            transcript: OpenAI transcript object
            
        Returns:
            List of segments with timing
        """
        segments = []
        
        if hasattr(transcript, 'segments'):
            for segment in transcript.segments:
                segments.append({
                    "id": cls._segment_value(segment, "id", 0),
                    "seek": cls._segment_value(segment, "seek", 0),
                    "start": cls._segment_value(segment, "start", 0),
                    "end": cls._segment_value(segment, "end", 0),
                    "text": cls._segment_value(segment, "text", ""),
                    "tokens": cls._segment_value(segment, "tokens", []),
                    "temperature": cls._segment_value(segment, "temperature", 0),
                    "avg_logprob": cls._segment_value(segment, "avg_logprob", 0),
                    "compression_ratio": cls._segment_value(segment, "compression_ratio", 0),
                    "no_speech_prob": cls._segment_value(segment, "no_speech_prob", 0)
                })
        
        return segments
