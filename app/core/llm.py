"""
Central LLM client factory for LinguaForge.

All code that needs to talk to the language model (agents, routers,
future tool-calling loops) MUST go through this module. This is the
single source of truth for the local OpenAI-compatible endpoint
(vLLM, llama.cpp server, Ollama, etc.).

Usage:
    from app.core.llm import get_llm_client, get_async_llm_client

    client = get_llm_client()
    response = client.chat.completions.create(...)

    # or async
    aclient = get_async_llm_client()
    response = await aclient.chat.completions.create(...)
"""
from openai import OpenAI, AsyncOpenAI
from app.core.config import settings
from functools import lru_cache


@lru_cache(maxsize=1)
def get_llm_client() -> OpenAI:
    """
    Return a cached synchronous OpenAI client configured for the local
    model server defined in settings.
    """
    return OpenAI(
        base_url=settings.AI_BASE_URL,
        api_key="not-needed-for-local",  # local servers usually ignore this
    )


@lru_cache(maxsize=1)
def get_async_llm_client() -> AsyncOpenAI:
    """
    Return a cached asynchronous OpenAI client configured for the local
    model server defined in settings.
    """
    return AsyncOpenAI(
        base_url=settings.AI_BASE_URL,
        api_key="not-needed-for-local",
    )


def get_model_name() -> str:
    """Convenience accessor for the model name used in completions."""
    return settings.AI_MODEL
