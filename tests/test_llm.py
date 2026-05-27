import pytest
from app.core.llm import get_llm_client, get_async_llm_client, get_model_name
from app.core.config import settings


def test_llm_client_created_with_correct_base_url():
    client = get_llm_client()
    # The underlying httpx client stores the base_url
    assert settings.AI_BASE_URL in str(client.base_url)
    assert client.api_key == "not-needed-for-local"


def test_async_llm_client_created_with_correct_base_url():
    aclient = get_async_llm_client()
    assert settings.AI_BASE_URL in str(aclient.base_url)


def test_get_model_name_returns_config_value():
    model = get_model_name()
    assert model == settings.AI_MODEL
    assert model  # not empty
