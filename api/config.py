"""Centralized configuration for the summarize API."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in parent directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Validate required environment variables
REQUIRED_ENV_VARS = ["OPENROUTER_API_KEY"]
for var in REQUIRED_ENV_VARS:
    if not os.getenv(var):
        raise ValueError(f"{var} environment variable is required")

# API Configuration
API_PORT = int(os.getenv("API_PORT", "3669"))
API_HOST = os.getenv("API_HOST", "0.0.0.0")

# Database
DATABASE_PATH = Path(os.getenv("DATABASE_PATH", "summarize.db"))

# File Storage
TEMP_DIR = Path(os.getenv("TEMP_DIR", "temp"))
TEMP_DIR.mkdir(parents=True, exist_ok=True)

# Processing
POLLING_INTERVAL = int(os.getenv("POLLING_INTERVAL", "5"))

# Audio Settings
AUDIO_SAMPLE_RATE = int(os.getenv("AUDIO_SAMPLE_RATE", "16000"))
MP3_QUALITY = os.getenv("MP3_QUALITY", "192")

# Whisper Configuration
WHISPER_BASE_DIR = Path(os.getenv("WHISPER_BASE_DIR", "whisper.cpp"))
WHISPER_BINARY = WHISPER_BASE_DIR / "build/bin/whisper-cli"
WHISPER_MODEL = WHISPER_BASE_DIR / "models/ggml-large-v3-turbo.bin"
WHISPER_ENTROPY_THRESHOLD = float(os.getenv("WHISPER_ENTROPY_THRESHOLD", "2.8"))
WHISPER_BEAM_SIZE = int(os.getenv("WHISPER_BEAM_SIZE", "5"))
WHISPER_MAX_CONTEXT = int(os.getenv("WHISPER_MAX_CONTEXT", "64"))

# LLM Configuration
LLM_API_KEY = os.getenv("OPENROUTER_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "openai/gpt-5-nano")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))
LLM_MAX_TOKENS = int(os.getenv("LLM_MAX_TOKENS", "16384"))
