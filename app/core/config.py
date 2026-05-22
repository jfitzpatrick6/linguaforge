from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    # AI Endpoint Configuration
    AI_BASE_URL: str
    AI_MODEL: str
    
    # Database Configuration
    DATABASE_URL: str = "sqlite+aiosqlite:///./app.db"
    DEBUG: bool = False
    
    # Data Paths
    CHROMA_PATH: str = "./data/chroma"
    SUPPORTED_LANGUAGES_DIR: Path = Path("supported_languages")
    
    # Optional: Set to True to use vLLM or other OpenAI-compatible API
    USE_VLLM: bool = False
    
    class Config:
        env_file = ".env.example"
        env_file_encoding = "utf-8"

settings = Settings()