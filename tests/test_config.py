import pytest
from app.config import Settings


def test_settings_loads_correctly():
    settings = Settings()
    assert settings.debug is False
    assert settings.database_url == "sqlite+aiosqlite:///:memory:"
    assert settings.openai_api_key is not None
    assert settings.llm_model == "gpt-4o"
    assert settings.max_tokens == 4096
    assert settings.temperature == 0.7
    assert settings.max_retries == 3
    assert settings.cache_enabled is True
    assert settings.cache_ttl == 3600
    assert settings.allowed_origins == ["*"], "Allowed origins should include wildcard"
    assert settings.log_level == "INFO"
    assert settings.log_file == "logs/app.log"
    assert settings.max_file_size_mb == 10
    assert settings.max_concurrent_users == 1000
