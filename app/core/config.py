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

    # Vector store (Chroma)
    CHROMA_PATH: str = "./data/chroma"

    # Local embedding model for RAG grounding (sentence-transformers)
    # Good multilingual option: "paraphrase-multilingual-MiniLM-L12-v2"
    # Faster English-strong default: "all-MiniLM-L6-v2"
    EMBEDDING_MODEL: str = "paraphrase-multilingual-MiniLM-L12-v2"

settings = Settings()