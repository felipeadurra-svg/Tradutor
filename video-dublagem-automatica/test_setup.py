"""
Script de teste para validar a instalação do projeto
Usage: python test_setup.py
"""

import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def check_python_version():
    """Check Python version"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        logger.info(f"✓ Python version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        logger.error(f"✗ Python 3.9+ required, found {version.major}.{version.minor}")
        return False


def check_command_exists(command):
    """Check if a command exists in PATH"""
    result = subprocess.run(
        ['which', command] if sys.platform != 'win32' else ['where', command],
        capture_output=True,
        text=True
    )
    return result.returncode == 0


def check_system_tools():
    """Check required system tools"""
    tools = ['ffmpeg', 'ffprobe', 'yt-dlp']
    all_ok = True
    
    for tool in tools:
        if check_command_exists(tool):
            logger.info(f"✓ {tool} found")
        else:
            logger.error(f"✗ {tool} not found")
            all_ok = False
    
    return all_ok


def check_python_packages():
    """Check required Python packages"""
    try:
        import fastapi
        logger.info("✓ FastAPI installed")
        
        import uvicorn
        logger.info("✓ Uvicorn installed")
        
        import openai
        logger.info("✓ OpenAI installed")
        
        import yt_dlp
        logger.info("✓ yt-dlp installed")
        
        import ffmpeg
        logger.info("✓ ffmpeg-python installed")
        
        import google.auth
        logger.info("✓ google-auth installed")
        
        return True
    except ImportError as e:
        logger.error(f"✗ Missing package: {str(e)}")
        return False


def check_env_file():
    """Check .env file"""
    if os.path.exists('.env'):
        logger.info("✓ .env file exists")
        
        # Check for OPENAI_API_KEY
        with open('.env', 'r') as f:
            content = f.read()
            if 'OPENAI_API_KEY=' in content:
                if 'your_openai_api_key_here' not in content:
                    logger.info("✓ OPENAI_API_KEY configured")
                else:
                    logger.warning("⚠ OPENAI_API_KEY not configured")
                    return False
        return True
    else:
        logger.error("✗ .env file not found")
        logger.info("  Copy .env.example to .env and configure")
        return False


def check_directories():
    """Check required directories"""
    dirs = ['storage/input', 'storage/audio', 'storage/output', 'credentials']
    all_ok = True
    
    for d in dirs:
        if os.path.isdir(d):
            logger.info(f"✓ Directory {d} exists")
        else:
            logger.error(f"✗ Directory {d} missing")
            all_ok = False
    
    return all_ok


def main():
    """Run all checks"""
    logger.info("=" * 60)
    logger.info("Video Dublagem Automática - Setup Check")
    logger.info("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("System Tools", check_system_tools),
        ("Python Packages", check_python_packages),
        ("Environment Config", check_env_file),
        ("Directories", check_directories),
    ]
    
    results = []
    for name, check_func in checks:
        logger.info(f"\nChecking {name}...")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"Error checking {name}: {str(e)}")
            results.append((name, False))
    
    logger.info("\n" + "=" * 60)
    logger.info("Summary:")
    for name, result in results:
        status = "✓" if result else "✗"
        logger.info(f"  {status} {name}")
    
    logger.info("=" * 60)
    
    if all(result for _, result in results):
        logger.info("✓ All checks passed! System is ready.")
        logger.info("\nTo start the server, run:")
        logger.info("  uvicorn app.main:app --reload")
        logger.info("\nAPI will be available at:")
        logger.info("  http://localhost:8000")
        logger.info("  http://localhost:8000/docs (Swagger)")
        return 0
    else:
        logger.error("✗ Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
