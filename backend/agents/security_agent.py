"""Security agent — OWASP Top 10, SQL injection, XSS, hardcoded secrets, auth flaws."""

from __future__ import annotations

from typing import Any

from backend.agents.base_agent import BaseAgent
from backend.models.schemas import Finding


class SecurityAgent(BaseAgent):
    """Agent specialised in security vulnerabilities."""

    def __init__(self) -> None:
        super().__init__(
            name="security",
            role_description=(
                "cybersecurity and OWASP Top 10. I also keep tabs on general tech and can riff on anything with a security-minded twist."
            ),
        )

    async def analyze(
        self,
        code: str,
        context: list[dict[str, Any]] | None = None,
        round: int = 1,
    ) -> list[Finding]:
        """Analyse code for security issues."""
        user_prompt = self._build_user_prompt(code, context, round)
        raw = await self._call_llm(user_prompt)
        return self._parse_findings(raw, round)
