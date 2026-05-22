from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Any


class Settings(BaseSettings):
    """Application settings loaded from .env"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="allow",
        case_sensitive=False,
    )

    # AI Endpoint Configuration
    AI_BASE_URL: str = "http://localhost:8000/v1"
    AI_MODEL: str = "qwen3-coder-30b-a3b"
    # Database Configuration
    DB_PATH: str = "./data/linguaforge.db"
    CHROMA_PATH: str = "./data/chroma"
    DEBUG: bool = False
    
    # Data Paths
    SUPPORTED_LANGUAGES_DIR: Path = Path("supported_languages")
    
    # Optional: Set to True to use vLLM or other OpenAI-compatible API
    USE_VLLM: bool = False
    
    def __init__(self, **data: Any) -> None:
        super().__init__(**data)
        # Ensure data directory exists
        import os
        os.makedirs("data", exist_ok=True)
settings = Settings()