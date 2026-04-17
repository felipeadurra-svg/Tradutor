import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent.parent
STORAGE_DIR = BASE_DIR / "storage"
INPUT_DIR = STORAGE_DIR / "input"
AUDIO_DIR = STORAGE_DIR / "audio"
OUTPUT_DIR = STORAGE_DIR / "output"
CREDENTIALS_DIR = BASE_DIR / "credentials"

# Ensure directories exist
for directory in [INPUT_DIR, AUDIO_DIR, OUTPUT_DIR, CREDENTIALS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
YOUTUBE_CREDENTIALS_FILE = os.getenv("YOUTUBE_CREDENTIALS_FILE", str(CREDENTIALS_DIR / "client_secret.json"))

# Settings
LANGUAGE_TARGET = "pt-BR"
LANGUAGE_SOURCE = "en"
MAX_WORKERS = 4
CHUNK_SIZE = 1024 * 1024  # 1MB chunks for downloads

# FFmpeg
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")
FFPROBE_PATH = os.getenv("FFPROBE_PATH", "ffprobe")

# OpenAI Settings
WHISPER_MODEL = "whisper-1"
GPT_MODEL = "gpt-4"
TTS_MODEL = "tts-1-hd"
TTS_VOICE = "nova"

# Video Settings
VIDEO_CODEC = "libx264"
AUDIO_CODEC = "aac"
AUDIO_BITRATE = "192k"
AUDIO_SAMPLE_RATE = 44100

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Server
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
