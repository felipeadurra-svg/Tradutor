import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional, List
import subprocess
from datetime import datetime

logger = logging.getLogger(__name__)

from app.config.settings import OUTPUT_DIR, AUDIO_DIR
from app.utils.ffmpeg import FFmpegHandler, FFmpegError


class VideoProcessingError(Exception):
    """Raised when video processing fails"""
    pass


class VideoProcessor:
    """Handles video processing, audio extraction, and video generation"""

    @staticmethod
    def extract_audio_from_video(
        video_path: str,
        output_audio_path: Optional[str] = None
    ) -> str:
        """
        Extract audio track from video file
        
        Args:
            video_path: Path to input video
            output_audio_path: Path to save extracted audio
            
        Returns:
            Path to extracted audio file
        """
        try:
            logger.info(f"Extracting audio from {video_path}")
            
            if not output_audio_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_audio_path = str(AUDIO_DIR / f"extracted_audio_{timestamp}.wav")
            
            FFmpegHandler.extract_audio(video_path, output_audio_path)
            
            logger.info(f"Audio extracted successfully: {output_audio_path}")
            return output_audio_path
            
        except FFmpegError as e:
            logger.error(f"Failed to extract audio: {str(e)}")
            raise VideoProcessingError(f"Failed to extract audio: {str(e)}")

    @staticmethod
    def create_dubbed_video(
        original_video_path: str,
        dubbed_audio_path: str,
        output_video_path: Optional[str] = None,
        sync_offset: float = 0.0
    ) -> str:
        """
        Create dubbed video by replacing audio track
        
        Args:
            original_video_path: Path to original video
            dubbed_audio_path: Path to dubbed audio
            output_video_path: Path to save output video
            sync_offset: Sync offset in seconds
            
        Returns:
            Path to dubbed video
        """
        try:
            logger.info(f"Creating dubbed video")
            
            if not output_video_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_video_path = str(OUTPUT_DIR / f"dubbed_video_{timestamp}.mp4")
            
            Path(output_video_path).parent.mkdir(parents=True, exist_ok=True)
            
            FFmpegHandler.replace_audio(
                original_video_path,
                dubbed_audio_path,
                output_video_path,
                sync_offset=sync_offset
            )
            
            logger.info(f"Dubbed video created successfully: {output_video_path}")
            return output_video_path
            
        except FFmpegError as e:
            logger.error(f"Failed to create dubbed video: {str(e)}")
            raise VideoProcessingError(f"Failed to create dubbed video: {str(e)}")

    @staticmethod
    def merge_audio_files(
        audio_files: List[str],
        output_path: Optional[str] = None
    ) -> str:
        """
        Merge multiple audio files into single audio track
        
        Args:
            audio_files: List of audio file paths
            output_path: Path to save merged audio
            
        Returns:
            Path to merged audio file
        """
        try:
            logger.info(f"Merging {len(audio_files)} audio files")
            
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = str(AUDIO_DIR / f"merged_audio_{timestamp}.wav")
            
            # Create concat demuxer file
            concat_file = str(AUDIO_DIR / "concat.txt")
            with open(concat_file, 'w') as f:
                for audio_file in audio_files:
                    f.write(f"file '{os.path.abspath(audio_file)}'\n")
            
            # Merge using ffmpeg
            command = [
                "ffmpeg",
                "-f", "concat",
                "-safe", "0",
                "-i", concat_file,
                "-c", "copy",
                "-y",
                output_path
            ]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=3600
            )
            
            # Clean up concat file
            if os.path.exists(concat_file):
                os.remove(concat_file)
            
            if result.returncode != 0:
                raise VideoProcessingError(f"Failed to merge audio: {result.stderr}")
            
            logger.info(f"Audio files merged successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error merging audio files: {str(e)}")
            raise VideoProcessingError(f"Failed to merge audio files: {str(e)}")

    @staticmethod
    def get_video_details(video_path: str) -> Dict[str, Any]:
        """
        Get detailed information about video file
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video details
        """
        try:
            logger.info(f"Getting video details for {video_path}")
            
            info = FFmpegHandler.get_video_info(video_path)
            duration = FFmpegHandler.get_duration(video_path)
            
            result = {
                "file_path": video_path,
                "file_size": os.path.getsize(video_path),
                "duration": duration,
                "info": info
            }
            
            logger.info(f"Video details retrieved successfully")
            return result
            
        except Exception as e:
            logger.error(f"Error getting video details: {str(e)}")
            raise VideoProcessingError(f"Failed to get video details: {str(e)}")

    @staticmethod
    def cleanup_temp_files(file_paths: List[str]) -> Dict[str, bool]:
        """
        Clean up temporary files
        
        Args:
            file_paths: List of file paths to delete
            
        Returns:
            Dictionary with cleanup results
        """
        results = {}
        
        for file_path in file_paths:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    results[file_path] = True
                    logger.debug(f"Cleaned up: {file_path}")
                else:
                    results[file_path] = False
            except Exception as e:
                logger.error(f"Error deleting {file_path}: {str(e)}")
                results[file_path] = False
        
        return results

    @staticmethod
    def process_video_pipeline(
        video_path: str,
        segments_with_audio: List[Dict[str, Any]],
        output_path: Optional[str] = None
    ) -> str:
        """
        Complete pipeline: extract audio, process segments, merge, replace
        
        Args:
            video_path: Path to original video
            segments_with_audio: List of segments with audio files
            output_path: Path to save final video
            
        Returns:
            Path to final dubbed video
        """
        try:
            logger.info("Starting complete video processing pipeline")
            
            # Extract video duration info
            video_info = VideoProcessor.get_video_details(video_path)
            duration = video_info["duration"]
            
            logger.info(f"Video duration: {duration} seconds")
            
            # Sort segments by start time
            sorted_segments = sorted(
                segments_with_audio,
                key=lambda x: x.get('start', 0)
            )
            
            # Get audio files in order
            audio_files = [
                seg.get('audio_path')
                for seg in sorted_segments
                if seg.get('audio_path') and os.path.exists(seg.get('audio_path'))
            ]
            
            if not audio_files:
                raise VideoProcessingError("No audio files to process")
            
            logger.info(f"Processing {len(audio_files)} audio segments")
            
            # Merge all audio segments
            merged_audio = VideoProcessor.merge_audio_files(audio_files)
            
            # Create final dubbed video
            final_video = VideoProcessor.create_dubbed_video(
                video_path,
                merged_audio,
                output_path
            )
            
            logger.info(f"Video processing pipeline completed successfully")
            
            return final_video
            
        except Exception as e:
            logger.error(f"Error in video processing pipeline: {str(e)}")
            raise VideoProcessingError(f"Failed video processing pipeline: {str(e)}")
