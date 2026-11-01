import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "HindiVoice AI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Model Configuration
    MODEL_NAME: str = "ai4bharat/indic-parler-tts"
    DEVICE: str = "cpu"  # Autodetects cuda if available in tts_engine
    MAX_TEXT_LENGTH: int = 3000
    SAMPLING_RATE: int = 24000  # Default sampling rate for Indic Parler-TTS

    # Storage paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
    AUDIO_STORAGE_DIR: Path = BASE_DIR / "generated_audio"
    AUDIO_RETENTION_HOURS: int = 24
    CLEANUP_INTERVAL_MINUTES: int = 60

    # Gemini AI Cloud TTS Configuration
    GEMINI_API_KEY: str = ""
    GEMINI_TTS_MODEL: str = "gemini-3.8-flash-tts"

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

    model_config = SettingsConfigDict(
        env_file=[
            str(Path(__file__).resolve().parent.parent.parent.parent / ".env"),
            str(Path(__file__).resolve().parent.parent.parent / ".env"),
            ".env",
        ],
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

# Ensure storage directory exists
settings.AUDIO_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
