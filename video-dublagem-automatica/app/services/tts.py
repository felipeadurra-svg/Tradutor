import logging
from typing import Dict, Any, Optional
from pathlib import Path
from openai import OpenAI

logger = logging.getLogger(__name__)

from app.config.settings import OPENAI_API_KEY, TTS_MODEL, TTS_VOICE, AUDIO_DIR


class TTSError(Exception):
    """Raised when TTS generation fails"""
    pass


class TTSService:
    """Handles text-to-speech generation using OpenAI TTS"""

    def __init__(self):
        if not OPENAI_API_KEY:
            raise TTSError("OPENAI_API_KEY not configured")
        
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def generate_audio(
        self,
        text: str,
        output_path: str,
        voice: str = TTS_VOICE,
        speed: float = 1.0
    ) -> Dict[str, Any]:
        """
        Generate audio from text using OpenAI TTS
        
        Args:
            text: Text to convert to speech
            output_path: Path to save audio file
            voice: Voice to use (alloy, echo, fable, onyx, nova, shimmer)
            speed: Speech speed (0.25 to 4.0)
            
        Returns:
            Dictionary with generation info
        """
        try:
            logger.info(f"Generating TTS audio for {len(text)} characters")
            
            # Validate voice
            valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
            if voice not in valid_voices:
                logger.warning(f"Invalid voice {voice}, using nova")
                voice = "nova"
            
            # Validate speed
            if speed < 0.25 or speed > 4.0:
                logger.warning(f"Speed {speed} out of range, using 1.0")
                speed = 1.0
            
            response = self.client.audio.speech.create(
                model=TTS_MODEL,
                voice=voice,
                input=text,
                speed=speed
            )
            
            # Save audio file
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            response.stream_to_file(output_path)
            
            logger.info(f"TTS audio generated successfully: {output_path}")
            
            return {
                "success": True,
                "output_path": output_path,
                "voice": voice,
                "speed": speed,
                "text_length": len(text)
            }
            
        except Exception as e:
            logger.error(f"TTS generation error: {str(e)}")
            raise TTSError(f"Failed to generate audio: {str(e)}")

    def generate_segments_audio(
        self,
        segments: list,
        output_dir: str = str(AUDIO_DIR),
        voice: str = TTS_VOICE,
        speed: float = 1.0
    ) -> Dict[str, Any]:
        """
        Generate audio for multiple segments
        
        Args:
            segments: List of segments with translated_text
            output_dir: Directory to save audio files
            voice: Voice to use
            speed: Speech speed
            
        Returns:
            Dictionary with generation info and file paths
        """
        try:
            logger.info(f"Generating TTS audio for {len(segments)} segments")
            
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            generated_segments = []
            audio_files = []
            
            for i, segment in enumerate(segments):
                translated_text = segment.get('translated_text', '')
                
                if not translated_text.strip():
                    logger.warning(f"Segment {i} has empty text, skipping")
                    generated_segments.append({
                        **segment,
                        'audio_path': None,
                        'audio_generated': False
                    })
                    continue
                
                # Generate audio for segment
                output_file = Path(output_dir) / f"segment_{i:04d}.mp3"
                
                try:
                    self.generate_audio(
                        translated_text,
                        str(output_file),
                        voice=voice,
                        speed=speed
                    )
                    
                    generated_segments.append({
                        **segment,
                        'audio_path': str(output_file),
                        'audio_generated': True
                    })
                    
                    audio_files.append(str(output_file))
                    logger.debug(f"Generated audio for segment {i}")
                    
                except TTSError as e:
                    logger.error(f"Failed to generate audio for segment {i}: {str(e)}")
                    generated_segments.append({
                        **segment,
                        'audio_path': None,
                        'audio_generated': False,
                        'error': str(e)
                    })
            
            logger.info(f"Generated TTS audio for {len(audio_files)} segments")
            
            return {
                "success": True,
                "segments": generated_segments,
                "audio_files": audio_files,
                "output_directory": output_dir,
                "total_segments": len(segments),
                "successful": len(audio_files)
            }
            
        except Exception as e:
            logger.error(f"Error generating segment audio: {str(e)}")
            raise TTSError(f"Failed to generate segment audio: {str(e)}")

    def batch_generate_audio(
        self,
        texts: list,
        output_dir: str = str(AUDIO_DIR),
        voice: str = TTS_VOICE,
        speed: float = 1.0
    ) -> Dict[str, Any]:
        """
        Generate audio for multiple texts in batch
        
        Args:
            texts: List of text strings
            output_dir: Directory to save audio files
            voice: Voice to use
            speed: Speech speed
            
        Returns:
            Dictionary with generation info
        """
        try:
            logger.info(f"Batch generating TTS audio for {len(texts)} texts")
            
            Path(output_dir).mkdir(parents=True, exist_ok=True)
            
            audio_files = []
            
            for i, text in enumerate(texts):
                if not text.strip():
                    logger.warning(f"Text {i} is empty, skipping")
                    continue
                
                output_file = Path(output_dir) / f"batch_{i:04d}.mp3"
                
                try:
                    self.generate_audio(
                        text,
                        str(output_file),
                        voice=voice,
                        speed=speed
                    )
                    audio_files.append(str(output_file))
                    logger.debug(f"Generated audio {i}")
                except TTSError as e:
                    logger.error(f"Failed to generate audio {i}: {str(e)}")
            
            logger.info(f"Batch generation completed: {len(audio_files)}/{len(texts)} successful")
            
            return {
                "success": True,
                "audio_files": audio_files,
                "output_directory": output_dir,
                "total": len(texts),
                "successful": len(audio_files)
            }
            
        except Exception as e:
            logger.error(f"Error in batch generation: {str(e)}")
            raise TTSError(f"Failed batch generation: {str(e)}")
