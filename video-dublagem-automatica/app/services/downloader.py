import logging
import subprocess
import os
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

from app.config.settings import INPUT_DIR, CHUNK_SIZE


class DownloadError(Exception):
    """Raised when video download fails"""
    pass


class VideoDownloader:
    """Handles video download from various sources using yt-dlp"""

    @staticmethod
    def download_video(
        video_url: str,
        output_format: str = "best",
        max_retries: int = 3
    ) -> Dict[str, Any]:
        """
        Download video from URL
        
        Args:
            video_url: URL of the video to download
            output_format: Video format quality
            max_retries: Number of retry attempts
            
        Returns:
            Dictionary with download info and file path
        """
        try:
            logger.info(f"Starting download from {video_url}")
            
            # Generate output filename
            output_template = str(INPUT_DIR / "%(title)s_%(id)s.%(ext)s")
            
            command = [
                "yt-dlp",
                "-f", output_format,
                "-o", output_template,
                "-v" if logger.level == logging.DEBUG else "-q",
                "--no-warnings",
                video_url
            ]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=3600
            )
            
            if result.returncode != 0:
                logger.error(f"yt-dlp error: {result.stderr}")
                raise DownloadError(f"Failed to download video: {result.stderr}")
            
            # Find downloaded file
            downloaded_file = VideoDownloader._find_downloaded_file()
            
            if not downloaded_file:
                raise DownloadError("Downloaded file not found")
            
            logger.info(f"Video downloaded successfully to {downloaded_file}")
            
            return {
                "success": True,
                "file_path": str(downloaded_file),
                "file_name": downloaded_file.name,
                "file_size": downloaded_file.stat().st_size,
                "url": video_url
            }
            
        except subprocess.TimeoutExpired:
            raise DownloadError("Download timed out")
        except Exception as e:
            logger.error(f"Error downloading video: {str(e)}")
            raise

    @staticmethod
    def _find_downloaded_file() -> Optional[Path]:
        """
        Find the most recently downloaded file
        
        Returns:
            Path to the downloaded file or None
        """
        try:
            files = list(INPUT_DIR.glob("*"))
            if not files:
                return None
            
            # Get the most recent file
            latest_file = max(files, key=lambda p: p.stat().st_mtime)
            return latest_file
            
        except Exception as e:
            logger.error(f"Error finding downloaded file: {str(e)}")
            return None

    @staticmethod
    def get_video_info(video_url: str) -> Dict[str, Any]:
        """
        Get video information without downloading
        
        Args:
            video_url: URL of the video
            
        Returns:
            Dictionary with video information
        """
        try:
            logger.info(f"Getting info for {video_url}")
            
            command = [
                "yt-dlp",
                "-j",
                "-q",
                video_url
            ]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                raise DownloadError(f"Failed to get video info: {result.stderr}")
            
            import json
            info = json.loads(result.stdout)
            
            logger.info(f"Video info retrieved successfully")
            
            return {
                "title": info.get("title", "Unknown"),
                "duration": info.get("duration", 0),
                "upload_date": info.get("upload_date", "Unknown"),
                "uploader": info.get("uploader", "Unknown"),
                "url": video_url
            }
            
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            raise

    @staticmethod
    def cleanup_input_file(file_path: str) -> bool:
        """
        Clean up downloaded input file
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if successful
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up input file: {file_path}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error cleaning up file: {str(e)}")
            return False
