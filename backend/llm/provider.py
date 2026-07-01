"""LLM Provider abstraction layer.

Allows swapping the underlying LLM provider (Qwen, OpenAI, Anthropic, etc.)
without changing agent code.

Usage:
    from backend.llm.provider import get_provider

    provider = get_provider()
    response = await provider.complete(
        model="qwen3-coder-plus",
        messages=[...],
        max_tokens=2048,
    )
"""

from __future__ import annotations

import asyncio
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from openai import AsyncOpenAI, APIStatusError, RateLimitError

from backend.config import settings

logger = logging.getLogger(__name__)

# Retry configuration
MAX_RETRIES = 3
INITIAL_BACKOFF_MS = 1000


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider."""

    content: str
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    model: str = ""


class LLMProvider(ABC):
    """Abstract interface for LLM providers."""

    @abstractmethod
    async def complete(
        self,
        model: str,
        messages: list[dict[str, str]],
        max_tokens: int = 2048,
        temperature: float = 0.3,
        **kwargs: Any,
    ) -> LLMResponse:
        """Send a chat completion request.

        Args:
            model: Model identifier (e.g. "qwen3-coder-plus").
            messages: List of message dicts with "role" and "content".
            max_tokens: Maximum tokens in the response.
            temperature: Sampling temperature (0.0-1.0).
            **kwargs: Provider-specific options.

        Returns:
            LLMResponse with content and token usage.
        """
        ...


class QwenProvider(LLMProvider):
    """Qwen Cloud API provider via OpenAI-compatible interface."""

    def __init__(self) -> None:
        self._client = AsyncOpenAI(
            api_key=settings.qwen_api_key,
            base_url=settings.qwen_base_url,
            timeout=settings.qwen_timeout_seconds,
        )

    async def complete(
        self,
        model: str,
        messages: list[dict[str, str]],
        max_tokens: int = 2048,
        temperature: float = 0.3,
        **kwargs: Any,
    ) -> LLMResponse:
        """Send a chat completion request to Qwen Cloud with retry on rate limits."""
        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                response = await self._client.chat.completions.create(
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    **kwargs,
                )

                content = response.choices[0].message.content or ""
                usage = response.usage

                return LLMResponse(
                    content=content,
                    input_tokens=usage.prompt_tokens if usage else 0,
                    output_tokens=usage.completion_tokens if usage else 0,
                    total_tokens=usage.total_tokens if usage else 0,
                    model=model,
                )

            except RateLimitError as e:
                last_error = e
                backoff = (INITIAL_BACKOFF_MS * (2 ** attempt)) / 1000
                logger.warning(
                    "Qwen rate limited (attempt %d/%d). Retrying in %.1fs...",
                    attempt + 1, MAX_RETRIES, backoff,
                )
                await asyncio.sleep(backoff)

            except APIStatusError as e:
                if e.status_code == 429:
                    last_error = e
                    backoff = (INITIAL_BACKOFF_MS * (2 ** attempt)) / 1000
                    logger.warning(
                        "Qwen rate limited via 429 (attempt %d/%d). Retrying in %.1fs...",
                        attempt + 1, MAX_RETRIES, backoff,
                    )
                    await asyncio.sleep(backoff)
                else:
                    logger.error("Qwen API error %d: %s", e.status_code, str(e)[:200])
                    return LLMResponse(content="NO_FINDINGS", model=model)

            except Exception as e:
                logger.error("Qwen LLM call failed: %s: %s", type(e).__name__, str(e)[:200])
                return LLMResponse(content="NO_FINDINGS", model=model)

        logger.error("All %d retries exhausted. Last error: %s", MAX_RETRIES, last_error)
        return LLMResponse(content="NO_FINDINGS", model=model)


# ──────────────────────────────────────────────
#  Singleton
# ──────────────────────────────────────────────

_provider: LLMProvider | None = None


def get_provider() -> LLMProvider:
    """Get the global LLM provider singleton."""
    global _provider
    if _provider is None:
        _provider = QwenProvider()
    return _provider


def set_provider(provider: LLMProvider) -> None:
    """Set a custom LLM provider (for testing or swapping providers)."""
    global _provider
    _provider = provider
