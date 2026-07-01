"""Generalist agent — broad knowledge across science, tech, and life.

This agent answers ANY question (greetings, science, philosophy, tech)
with warmth and insight. It is the default agent for social/simple queries.
"""

from __future__ import annotations

from typing import Any

from backend.agents.base_agent import BaseAgent
from backend.models.schemas import Finding


class GeneralistAgent(BaseAgent):
    """Agent with broad general knowledge."""

    def __init__(self) -> None:
        super().__init__(
            name="generalist",
            role_description=(
                "a generalist with broad knowledge across science, technology, "
                "and life. I can answer any question with wisdom and a touch of wit. "
                "I'm the friend who always has something interesting to say."
            ),
        )

    async def analyze(
        self,
        code: str,
        context: list[dict[str, Any]] | None = None,
        round: int = 1,
    ) -> list[Finding]:
        """Generalist agent does NOT do code review — returns empty findings."""
        return []
