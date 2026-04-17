"""
Development utilities and helpers for the project
"""

import os
import json
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


def create_sample_response() -> Dict[str, Any]:
    """Create a sample API response for testing"""
    return {
        "success": True,
        "message": "Sample response for testing",
        "status": "completed",
        "video_id": "dQw4w9WgXcQ",
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "local_file_path": "/path/to/dubbed_video.mp4",
        "transcription": "Sample transcription text",
        "duration": 600.0
    }


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('app.log')
        ]
    )


def validate_env_file() -> bool:
    """Validate .env file configuration"""
    if not os.path.exists('.env'):
        logger.error(".env file not found")
        return False
    
    required_vars = ['OPENAI_API_KEY']
    
    with open('.env', 'r') as f:
        content = f.read()
    
    for var in required_vars:
        if var not in content:
            logger.error(f"Missing {var} in .env")
            return False
        
        # Check if value is set
        lines = content.split('\n')
        for line in lines:
            if line.startswith(var):
                value = line.split('=', 1)[1].strip()
                if not value or value == 'your_openai_api_key_here':
                    logger.error(f"{var} value not set")
                    return False
    
    return True


def cleanup_storage(older_than_hours: int = 24) -> Dict[str, int]:
    """Clean up old files from storage directories"""
    import time
    from pathlib import Path
    
    cleanup_stats = {
        "files_deleted": 0,
        "bytes_freed": 0,
        "errors": 0
    }
    
    storage_dirs = [
        Path("storage/input"),
        Path("storage/audio"),
        Path("storage/output")
    ]
    
    current_time = time.time()
    cutoff_time = current_time - (older_than_hours * 3600)
    
    for storage_dir in storage_dirs:
        if not storage_dir.exists():
            continue
        
        for file_path in storage_dir.glob("*"):
            if file_path.is_file():
                file_mtime = file_path.stat().st_mtime
                
                if file_mtime < cutoff_time:
                    try:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        cleanup_stats["files_deleted"] += 1
                        cleanup_stats["bytes_freed"] += file_size
                        logger.info(f"Cleaned up: {file_path}")
                    except Exception as e:
                        cleanup_stats["errors"] += 1
                        logger.error(f"Error cleaning {file_path}: {str(e)}")
    
    return cleanup_stats


def get_storage_stats() -> Dict[str, Any]:
    """Get storage usage statistics"""
    from pathlib import Path
    import os
    
    stats = {
        "total_size_mb": 0,
        "directories": {}
    }
    
    storage_dirs = [
        ("input", Path("storage/input")),
        ("audio", Path("storage/audio")),
        ("output", Path("storage/output"))
    ]
    
    for name, path in storage_dirs:
        if not path.exists():
            stats["directories"][name] = {
                "size_mb": 0,
                "file_count": 0
            }
            continue
        
        total_size = 0
        file_count = 0
        
        for file_path in path.glob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
                file_count += 1
        
        size_mb = total_size / (1024 * 1024)
        stats["directories"][name] = {
            "size_mb": round(size_mb, 2),
            "file_count": file_count
        }
        stats["total_size_mb"] += size_mb
    
    stats["total_size_mb"] = round(stats["total_size_mb"], 2)
    return stats


if __name__ == "__main__":
    # Example usage
    print("Development utilities loaded")
    print("Use: from utils import *")
