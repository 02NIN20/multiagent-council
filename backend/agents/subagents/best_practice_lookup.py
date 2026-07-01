"""BestPracticeLookup sub-agent — looks up best practices for topics."""

from __future__ import annotations

from typing import Any

from backend.agents.subagents.base_subagent import BaseSubAgent


class BestPracticeLookup(BaseSubAgent):
    """Looks up best practices for development topics."""

    def __init__(self) -> None:
        super().__init__(
            name="best_practice_lookup",
            specialty="looking up best practices for development topics",
        )

    async def lookup(self, topic: str, context: str = "") -> dict[str, Any]:
        """Looks up best practices.

        Parameters
        ----------
        topic : str
            The topic or technology to look up best practices for.
        context : str
            Additional context about the specific use case.

        Returns
        -------
        dict with keys: summary, practices, references.
        """
        if not topic.strip():
            return {"summary": "", "practices": [], "references": []}

        prompt = (
            f"Look up and summarize best practices for the topic: {topic}.\n\n"
            f"Context: {context}\n\n"
            f"Provide best practices covering:\n"
            f"1. Overview and principles\n"
            f"2. Common patterns and anti-patterns\n"
            f"3. Implementation recommendations\n"
            f"4. Testing and validation approaches\n"
            f"5. Tools and frameworks that support these practices\n\n"
            f"Return a JSON object with:\n"
            f"- summary: brief overview\n"
            f"- practices: array of practice objects, each with name and description\n"
            f"- references: array of resource URLs or references\n"
            f"\nReturn only valid JSON, no other text."
        )

        response = await self._call_llm(
            system_prompt="You are a best practices expert. Provide comprehensive, up-to-date development best practices and guidelines.",
            user_prompt=prompt,
            max_tokens=2048,
            temperature=0.2,
        )

        import json
        try:
            result = json.loads(response)
            return {
                "summary": result.get("summary", ""),
                "practices": result.get("practices", []),
                "references": result.get("references", []),
            }
        except (json.JSONDecodeError, TypeError):
            return {
                "summary": f"Best practices for {topic}",
                "practices": [
                    {"name": "Follow established patterns", "description": "Use proven patterns and conventions"},
                    {"name": "Write clean code", "description": "Follow PEP 8 and naming conventions"},
                    {"name": "Test thoroughly", "description": "Write unit tests and integration tests"},
                ],
                "references": [
                    "https://docs.python.org/3/styleguide/",
                    "https://en.wikipedia.org/wiki/Best_practices"
                ]
            }
