# app/gateway.py
from langchain_openai import ChatOpenAI
from openai import AsyncOpenAI, OpenAI
from portkey_ai import PORTKEY_GATEWAY_URL, createHeaders
from app.configs.config import settings



def _make_headers(feature: str = "rag") -> dict:
    """Build Portkey headers that reference the primary saved config by ID."""
    if not settings.PORTKEY_API_KEY or not settings.PORTKEY_PRIMARY_CONFIG_ID:
        raise ValueError(
            "PORTKEY_API_KEY and PORTKEY_PRIMARY_CONFIG_ID must be set in the environment."
        )
    
    return createHeaders(
        api_key=settings.PORTKEY_API_KEY,
        config_id=settings.PORTKEY_PRIMARY_CONFIG_ID,
        metadata={
            "feature": feature,
            "_user": "enterprise_rag_app",
            "environment": "production",
        },
    )


def get_langchain_llm(feature: str = "rag") -> ChatOpenAI:
    """Get a LangChain LLM client that uses the Portkey Gateway."""
    return ChatOpenAI(
        api_key=settings.PORTKEY_API_KEY,
        base_url=PORTKEY_GATEWAY_URL,
        model=f"@{settings.PORTKEY_PRIMARY_SLUG}/llama-3.1-70b-versatile",
        default_headers=_make_headers(feature=feature),
    )


def get_async_client(feature: str = "rag") -> AsyncOpenAI:
    """Returns an async client for non-blocking web requests."""
    return AsyncOpenAI(
        api_key=settings.PORTKEY_API_KEY,
        base_url=PORTKEY_GATEWAY_URL,
        default_headers=_make_headers(feature),
    )


def get_sync_client(feature: str = "rag") -> OpenAI:
    """Returns a raw, synchronous OpenAI client."""
    return OpenAI(
        api_key=settings.PORTKEY_API_KEY,
        base_url=PORTKEY_GATEWAY_URL,
        default_headers=_make_headers(feature),
    )


def extract_cache_status(response) -> str:
    """Checks if the response came from Portkey's cache."""
    attributes = ("_raw_response", "_response", "_http_response", "headers")
    for attr in attributes:
        raw = getattr(response, attr, None)
        if raw is not None:
            headers = getattr(raw, "headers", None)
            if headers is not None:
                status = headers.get("x-portkey-cache-status", "")
                if status:
                    return status.upper()
    return "MISS"