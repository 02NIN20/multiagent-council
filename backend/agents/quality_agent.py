"""Quality agent — code style, dead code, cyclomatic complexity, missing tests."""

from __future__ import annotations

from typing import Any

from backend.agents.base_agent import BaseAgent
from backend.models.schemas import Finding


class QualityAgent(BaseAgent):
    """Agent specialised in code quality."""

    def __init__(self) -> None:
        super().__init__(
            name="quality",
            role_description=(
                "calidad de código y buenas prácticas de ingeniería de software. "
                "Buscas: código muerto, estilo inconsistente, complejidad ciclomática alta, "
                "funciones demasiado largas, falta de tests, violaciones de convenciones, "
                "y código que no sigue el principio de responsabilidad única."
            ),
        )

    async def analyze(
        self,
        code: str,
        context: list[dict[str, Any]] | None = None,
        round: int = 1,
    ) -> list[Finding]:
        """Analyse code for quality issues."""
        user_prompt = self._build_user_prompt(code, context, round)
        raw = await self._call_llm(user_prompt)
        return self._parse_findings(raw, round)
