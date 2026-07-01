"""Base class for all sub-agents.

Sub-agents are lightweight specialists that core agents delegate to.
They share the same LLM provider but have narrower focus.
"""

from __future__ import annotations

import logging
from typing import Any

from backend.llm.provider import get_provider

logger = logging.getLogger(__name__)


class BaseSubAgent:
    """Abstract base sub-agent.

    Parameters
    ----------
    name : str
        Unique sub-agent identifier.
    specialty : str
        Short description of the sub-agent's focus.
    """

    def __init__(self, name: str, specialty: str) -> None:
        self.name = name
        self.specialty = specialty
        self._last_token_usage: dict[str, int] = {}

    async def _call_llm(
        self,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.3,
    ) -> str:
        """Send a chat completion via the LLM provider."""
        provider = get_provider()
        response = await provider.complete(
            model=None,  # use default model
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=max_tokens,
            temperature=temperature,
        )
        if response.total_tokens > 0:
            self._last_token_usage = {
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "total_tokens": response.total_tokens,
            }
        return response.content or ""

    def get_token_usage(self) -> dict[str, int]:
        """Return token usage from the last LLM call."""
        return self._last_token_usage.copy()
