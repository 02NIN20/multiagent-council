"""Performance agent — N+1 queries, cache missing, inefficient loops, resource usage."""

from __future__ import annotations

from typing import Any

from backend.agents.base_agent import BaseAgent
from backend.models.schemas import Finding


class PerformanceAgent(BaseAgent):
    """Agent specialised in performance."""

    def __init__(self) -> None:
        super().__init__(
            name="performance",
            role_description=(
                "rendimiento y optimización de código. "
                "Buscas: consultas N+1, falta de caché, bucles ineficientes, "
                "uso excesivo de memoria, bottlenecks de rendimiento, "
                "operaciones bloqueantes en código async, y patrones que no escalan."
            ),
        )

    async def analyze(
        self,
        code: str,
        context: list[dict[str, Any]] | None = None,
        round: int = 1,
    ) -> list[Finding]:
        """Analyse code for performance issues."""
        user_prompt = self._build_user_prompt(code, context, round)
        raw = await self._call_llm(user_prompt)
        return self._parse_findings(raw, round)
