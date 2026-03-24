"""ToolForge — App Configuration"""

from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "ToolForge"
    VERSION: str = "1.0.0"

    # File storage
    UPLOAD_DIR: str = "uploads"
    OUTPUT_DIR: str = "outputs"
    MAX_FILE_SIZE_MB: int = 100

    # Image
    MAX_IMAGE_DIMENSION: int = 16000  # px
    DEFAULT_IMAGE_QUALITY: int = 90

    # AI
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "qwen2.5:7b"
    WHISPER_MODEL: str = "base"


settings = Settings()
