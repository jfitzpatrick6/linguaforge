from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
        extra="allow",
        case_sensitive=False,
    )
    
    AI_BASE_URL: str = "http://localhost:8000/v1"
    AI_MODEL: str = "qwen3-coder-30b-a3b"
    DB_PATH: str = "./data/linguaforge.db"
    CHROMA_PATH: str = "./data/chroma"

settings = Settings()