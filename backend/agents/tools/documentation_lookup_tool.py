"""Tool to look up best practices and documentation references."""

from __future__ import annotations

from typing import Any

from backend.agents.tools.base_tool import BaseTool


class DocumentationLookupTool(BaseTool):
    """Look up best practices, patterns, and documentation references via LLM."""

    def __init__(self) -> None:
        super().__init__(
            name="documentation_lookup",
            description="Look up best practices, design patterns, and documentation for a given topic.",
        )

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """Look up information on a topic.

        Parameters
        ----------
        topic : str
            Topic to research (e.g. "SQL injection prevention", "REST API design").
        context : str, optional
            Additional context to refine the lookup.

        Returns
        -------
        dict with keys: summary (str), references (list), best_practices (list)
        """
        topic: str = kwargs.get("topic", "")
        context: str = kwargs.get("context", "")

        if not topic:
            return {"summary": "", "references": [], "best_practices": []}

        # Use the LLM to research the topic
        from backend.llm.provider import get_provider

        provider = get_provider()
        system_prompt = (
            "You are a technical documentation expert. Provide concise, accurate information "
            "about the requested topic. Focus on best practices, common patterns, and key references."
        )
        user_prompt = f"Topic: {topic}\n"
        if context:
            user_prompt += f"Context: {context}\n"
        user_prompt += (
            "\nProvide your response in this format:\n"
            "SUMMARY: <brief overview>\n"
            "BEST PRACTICES:\n"
            "- <practice 1>\n"
            "- <practice 2>\n"
            "REFERENCES:\n"
            "- <reference 1>\n"
        )

        response = await provider.complete(
            model=None,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=1024,
            temperature=0.2,
        )

        content = response.content or ""

        # Parse structured response
        summary = ""
        best_practices = []
        references = []

        lines = content.split("\n")
        current_section = None
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("SUMMARY:"):
                summary = stripped[len("SUMMARY:"):].strip()
            elif stripped.startswith("BEST PRACTICES:"):
                current_section = "practices"
            elif stripped.startswith("REFERENCES:"):
                current_section = "references"
            elif stripped.startswith("- ") and current_section == "practices":
                best_practices.append(stripped[2:])
            elif stripped.startswith("- ") and current_section == "references":
                references.append(stripped[2:])

        return {
            "summary": summary,
            "best_practices": best_practices,
            "references": references,
        }
