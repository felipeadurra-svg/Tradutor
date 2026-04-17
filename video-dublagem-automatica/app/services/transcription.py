import logging
import math
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from openai import OpenAI

logger = logging.getLogger(__name__)

from app.config.settings import AUDIO_DIR, OPENAI_API_KEY, WHISPER_MODEL, LANGUAGE_SOURCE, FFMPEG_PATH
from app.utils.ffmpeg import FFmpegHandler


class TranscriptionError(Exception):
    """Raised when transcription fails"""
    pass


class TranscriptionService:
    """Handles audio transcription using OpenAI Whisper"""

    MAX_UPLOAD_BYTES = 24 * 1024 * 1024
    CHUNK_BITRATE = "64k"
    CHUNK_SAMPLE_RATE = 16000
    MIN_CHUNK_SECONDS = 60
    MAX_CHUNK_SECONDS = 900

    def __init__(self):
        if not OPENAI_API_KEY:
            raise TranscriptionError("OPENAI_API_KEY not configured")
        
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def transcribe_audio(
        self,
        audio_path: str,
        language: str = LANGUAGE_SOURCE,
        progress_callback: Optional[Callable[[int, int], None]] = None
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

            audio_file_size = Path(audio_path).stat().st_size
            if audio_file_size <= self.MAX_UPLOAD_BYTES:
                if progress_callback:
                    progress_callback(0, 1)
                transcript = self._transcribe_file(audio_path, language)
                if progress_callback:
                    progress_callback(1, 1)
                return self._format_result(transcript, language)

            logger.info(
                "Audio exceeds direct upload limit (%.2f MB). Splitting into chunks.",
                audio_file_size / (1024 * 1024)
            )
            return self._transcribe_large_audio(audio_path, language, progress_callback)
            
        except FileNotFoundError:
            logger.error(f"Audio file not found: {audio_path}")
            raise TranscriptionError(f"Audio file not found: {audio_path}")
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            raise TranscriptionError(f"Failed to transcribe audio: {str(e)}")

    def _transcribe_file(self, audio_path: str, language: str):
        """Send a single audio file to the transcription API."""
        with open(audio_path, "rb") as audio_file:
            return self.client.audio.transcriptions.create(
                model=WHISPER_MODEL,
                file=audio_file,
                language=language,
                response_format="verbose_json"
            )

    def _format_result(self, transcript, language: str) -> Dict[str, Any]:
        """Normalize the SDK transcript object."""
        logger.info("Transcription completed successfully")
        return {
            "text": transcript.text,
            "language": transcript.language if hasattr(transcript, 'language') else language,
            "duration": transcript.duration if hasattr(transcript, 'duration') else 0,
            "segments": self._extract_segments(transcript)
        }

    def _transcribe_large_audio(
        self,
        audio_path: str,
        language: str,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Dict[str, Any]:
        """Split large audio files into smaller chunks and merge the results."""
        chunk_files: List[Dict[str, Any]] = []
        try:
            chunk_files = self._split_audio_for_transcription(audio_path)
            total_chunks = len(chunk_files)

            merged_texts: List[str] = []
            merged_segments: List[Dict[str, Any]] = []
            total_duration = 0.0

            for chunk_index, chunk_info in enumerate(chunk_files):
                if progress_callback:
                    progress_callback(chunk_index, total_chunks)
                logger.info(
                    "Transcribing chunk %s/%s starting at %.2fs",
                    chunk_index + 1,
                    total_chunks,
                    chunk_info["offset"]
                )
                transcript = self._transcribe_file(chunk_info["path"], language)
                chunk_result = self._format_result(transcript, language)

                chunk_text = chunk_result["text"].strip()
                if chunk_text:
                    merged_texts.append(chunk_text)

                offset = chunk_info["offset"]
                for segment in chunk_result["segments"]:
                    adjusted_segment = dict(segment)
                    adjusted_segment["id"] = len(merged_segments)
                    adjusted_segment["start"] = segment.get("start", 0) + offset
                    adjusted_segment["end"] = segment.get("end", 0) + offset
                    merged_segments.append(adjusted_segment)

                total_duration = max(total_duration, offset + chunk_result.get("duration", 0))

            if progress_callback:
                progress_callback(total_chunks, total_chunks)

            logger.info("Large audio transcription completed successfully")
            return {
                "text": " ".join(merged_texts).strip(),
                "language": language,
                "duration": total_duration,
                "segments": merged_segments
            }
        finally:
            self._cleanup_chunks(chunk_files)

    def _split_audio_for_transcription(self, audio_path: str) -> List[Dict[str, Any]]:
        """Create compressed chunks under the API upload limit."""
        audio_duration = FFmpegHandler.get_audio_duration(audio_path)
        audio_size = Path(audio_path).stat().st_size

        estimated_chunk_seconds = math.floor(
            audio_duration * (self.MAX_UPLOAD_BYTES / max(audio_size, 1)) * 0.9
        )
        chunk_duration = max(
            self.MIN_CHUNK_SECONDS,
            min(self.MAX_CHUNK_SECONDS, estimated_chunk_seconds)
        )

        if chunk_duration <= 0:
            raise TranscriptionError("Could not determine chunk duration for large audio")

        timestamp_prefix = Path(audio_path).stem
        chunk_count = math.ceil(audio_duration / chunk_duration)
        chunk_files: List[Dict[str, Any]] = []

        logger.info(
            "Splitting audio into %s chunk(s) of up to %s seconds",
            chunk_count,
            chunk_duration
        )

        for index in range(chunk_count):
            offset = index * chunk_duration
            output_path = AUDIO_DIR / f"{timestamp_prefix}_chunk_{index:03d}.mp3"
            self._create_audio_chunk(audio_path, str(output_path), offset, chunk_duration)

            chunk_size = output_path.stat().st_size
            if chunk_size > self.MAX_UPLOAD_BYTES:
                raise TranscriptionError(
                    f"Chunk {output_path.name} is still too large for transcription ({chunk_size} bytes)"
                )

            chunk_files.append({
                "path": str(output_path),
                "offset": offset
            })

        return chunk_files

    def _create_audio_chunk(
        self,
        input_path: str,
        output_path: str,
        offset_seconds: float,
        duration_seconds: int
    ) -> None:
        """Extract and compress one audio chunk for Whisper upload."""
        command = [
            FFMPEG_PATH,
            "-ss", str(offset_seconds),
            "-t", str(duration_seconds),
            "-i", input_path,
            "-vn",
            "-ac", "1",
            "-ar", str(self.CHUNK_SAMPLE_RATE),
            "-c:a", "libmp3lame",
            "-b:a", self.CHUNK_BITRATE,
            "-y",
            output_path
        ]

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=3600
        )

        if result.returncode != 0:
            raise TranscriptionError(f"Failed to create audio chunk: {result.stderr}")

    @staticmethod
    def _cleanup_chunks(chunk_files: List[Dict[str, Any]]) -> None:
        """Remove temporary chunk files created for transcription."""
        for chunk_info in chunk_files:
            chunk_path = Path(chunk_info["path"])
            try:
                if chunk_path.exists():
                    chunk_path.unlink()
            except Exception as exc:
                logger.warning("Could not remove temporary chunk %s: %s", chunk_path, exc)

    @staticmethod
    def _segment_value(segment: Any, key: str, default: Any = None) -> Any:
        """Read a segment field from either a dict-like or attribute-based SDK object."""
        if isinstance(segment, dict):
            return segment.get(key, default)

        return getattr(segment, key, default)

    @classmethod
    def _extract_segments(cls, transcript) -> List[Dict[str, Any]]:
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
