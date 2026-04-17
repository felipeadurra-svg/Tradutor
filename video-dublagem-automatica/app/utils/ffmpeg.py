import subprocess
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
import json

logger = logging.getLogger(__name__)

from app.config.settings import FFMPEG_PATH, FFPROBE_PATH, AUDIO_SAMPLE_RATE, AUDIO_BITRATE


class FFmpegError(Exception):
    """Raised when FFmpeg command fails"""
    pass


class FFmpegHandler:
    """Handles all FFmpeg operations for audio/video processing"""

    @staticmethod
    def extract_audio(
        video_path: str,
        audio_output_path: str,
        sample_rate: int = AUDIO_SAMPLE_RATE,
        audio_format: str = "wav"
    ) -> bool:
        """
        Extract audio from video file
        
        Args:
            video_path: Path to input video
            audio_output_path: Path to output audio file
            sample_rate: Audio sample rate (default 44100)
            audio_format: Audio format (default wav)
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Extracting audio from {video_path}")
            command = [
                FFMPEG_PATH,
                "-i", video_path,
                "-vn",
                "-acodec", "pcm_s16le",
                "-ar", str(sample_rate),
                "-ac", "2",
                "-q:a", "9",
                "-y",
                audio_output_path
            ]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=3600
            )
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                raise FFmpegError(f"Failed to extract audio: {result.stderr}")
            
            logger.info(f"Audio extracted successfully to {audio_output_path}")
            return True
            
        except subprocess.TimeoutExpired:
            raise FFmpegError("Audio extraction timed out")
        except Exception as e:
            logger.error(f"Error extracting audio: {str(e)}")
            raise

    @staticmethod
    def replace_audio(
        video_path: str,
        audio_path: str,
        output_path: str,
        sync_offset: float = 0.0
    ) -> bool:
        """
        Replace audio in video file with new audio
        
        Args:
            video_path: Path to original video
            audio_path: Path to new audio file
            output_path: Path to output video
            sync_offset: Offset in seconds to sync audio
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Replacing audio in {video_path}")
            
            command = [
                FFMPEG_PATH,
                "-i", video_path,
                "-i", audio_path,
                "-c:v", "copy",
                "-c:a", "aac",
                "-b:a", AUDIO_BITRATE,
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-y",
            ]
            
            # Add sync offset if needed
            if sync_offset != 0.0:
                # Apply delay to audio
                if sync_offset > 0:
                    command.extend(["-itsoffset", str(sync_offset)])
            
            command.append(output_path)
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=7200
            )
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                raise FFmpegError(f"Failed to replace audio: {result.stderr}")
            
            logger.info(f"Audio replaced successfully. Output: {output_path}")
            return True
            
        except subprocess.TimeoutExpired:
            raise FFmpegError("Audio replacement timed out")
        except Exception as e:
            logger.error(f"Error replacing audio: {str(e)}")
            raise

    @staticmethod
    def get_video_info(video_path: str) -> Dict[str, Any]:
        """
        Get video file information using ffprobe
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video information
        """
        try:
            logger.info(f"Getting video info for {video_path}")
            
            command = [
                FFPROBE_PATH,
                "-v", "error",
                "-show_format",
                "-show_streams",
                "-of", "json",
                video_path
            ]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise FFmpegError(f"Failed to get video info: {result.stderr}")
            
            info = json.loads(result.stdout)
            logger.info(f"Video info retrieved successfully")
            return info
            
        except json.JSONDecodeError:
            raise FFmpegError("Invalid video file or ffprobe output")
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            raise

    @staticmethod
    def get_duration(video_path: str) -> float:
        """
        Get video duration in seconds
        
        Args:
            video_path: Path to video file
            
        Returns:
            Duration in seconds
        """
        try:
            info = FFmpegHandler.get_video_info(video_path)
            duration = float(info["format"]["duration"])
            return duration
        except Exception as e:
            logger.error(f"Error getting duration: {str(e)}")
            raise

    @staticmethod
    def get_audio_duration(audio_path: str) -> float:
        """
        Get audio duration in seconds
        
        Args:
            audio_path: Path to audio file
            
        Returns:
            Duration in seconds
        """
        try:
            command = [
                FFPROBE_PATH,
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                audio_path
            ]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode != 0:
                raise FFmpegError(f"Failed to get audio duration: {result.stderr}")
            
            duration = float(result.stdout.strip())
            return duration
            
        except Exception as e:
            logger.error(f"Error getting audio duration: {str(e)}")
            raise

    @staticmethod
    def convert_audio_format(
        input_path: str,
        output_path: str,
        audio_format: str = "mp3",
        bitrate: str = "192k"
    ) -> bool:
        """
        Convert audio to different format
        
        Args:
            input_path: Path to input audio
            output_path: Path to output audio
            audio_format: Output format (mp3, aac, wav, etc)
            bitrate: Audio bitrate
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Converting audio to {audio_format}")
            
            command = [
                FFMPEG_PATH,
                "-i", input_path,
                "-ab", bitrate,
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
                raise FFmpegError(f"Failed to convert audio: {result.stderr}")
            
            logger.info(f"Audio converted successfully to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error converting audio: {str(e)}")
            raise

    @staticmethod
    def mux_audio_video(
        video_path: str,
        audio_path: str,
        output_path: str,
        video_codec: str = "copy",
        audio_codec: str = "aac"
    ) -> bool:
        """
        Mux (combine) audio and video streams
        
        Args:
            video_path: Path to video file
            audio_path: Path to audio file
            output_path: Path to output file
            video_codec: Video codec (copy for no re-encode)
            audio_codec: Audio codec
            
        Returns:
            True if successful
        """
        try:
            logger.info(f"Muxing video and audio")
            
            command = [
                FFMPEG_PATH,
                "-i", video_path,
                "-i", audio_path,
                "-c:v", video_codec,
                "-c:a", audio_codec,
                "-map", "0:v:0",
                "-map", "1:a:0",
                "-shortest",
                "-y",
                output_path
            ]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=7200
            )
            
            if result.returncode != 0:
                raise FFmpegError(f"Failed to mux streams: {result.stderr}")
            
            logger.info(f"Streams muxed successfully to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error muxing streams: {str(e)}")
            raise
