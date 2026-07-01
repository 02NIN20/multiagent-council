"""DocGenerator sub-agent — generates documentation for code."""

from __future__ import annotations

from typing import Any

from backend.agents.subagents.base_subagent import BaseSubAgent


class DocGenerator(BaseSubAgent):
    """Generates documentation and explanations for code."""

    def __init__(self) -> None:
        super().__init__(
            name="doc_generator",
            specialty="generating documentation and explanations for code",
        )

    async def generate_docs(self, code: str) -> str:
        """Generates documentation for code.

        Parameters
        ----------
        code : str
            Source code to document.

        Returns
        -------
        str
            Generated documentation.
        """
        if not code.strip():
            return ""

        prompt = (
            f"Generate comprehensive documentation for the following code.\n\n"
            f"Code:\n```\n{code[:3000]}\n```\n\n"
            f"Documentation should include:\n"
            f"1. Purpose and description of what the code does\n"
            f"2. Function signatures and parameters with types\n"
            f"3. Return values and their types\n"
            f"4. Usage examples\n"
            f"5. Dependencies and imports explained\n"
            f"6. Potential pitfalls or edge cases\n"
            f"7. Related concepts and context\n\n"
            f"Format the documentation in clean Markdown.\n"
            f"Generate only documentation, no additional commentary."
        )

        response = await self._call_llm(
            system_prompt="You are an expert technical writer. Generate clear, comprehensive documentation for code.",
            user_prompt=prompt,
            max_tokens=2048,
            temperature=0.2,
        )

        return response.strip()

    async def explain_code(self, code: str, finding: dict[str, Any]) -> str:
        """Explains a specific code section in context of a finding.

        Parameters
        ----------
        code : str
            Source code to explain.
        finding : dict
            Finding with context about what needs explanation.

        Returns
        -------
        str
            Explanation of the code in context of the finding.
        """
        if not code.strip():
            return ""

        title = finding.get("title", "") or finding.get("pattern", "")
        location = finding.get("location", "")
        severity = finding.get("severity", "")
        description = finding.get("description", "")

        prompt = (
            f"Explain the following code section in context of the finding.\n\n"
            f"Code:\n```\n{code[:2000]}\n```\n\n"
            f"Finding:\n"
            f"Title: {title}\n"
            f"Location: {location}\n"
            f"Severity: {severity}\n"
            f"Description: {description}\n\n"
            f"Explain:\n"
            f"1. What this code does and its purpose\n"
            f"2. How it relates to the finding\n"
            f"3. Why it's significant\n"
            f"4. Any additional context or implications\n\n"
            f"Provide a clear, concise explanation."
        )

        response = await self._call_llm(
            system_prompt="You are a code explanation expert. Explain code sections clearly in context of findings.",
            user_prompt=prompt,
            max_tokens=1536,
            temperature=0.2,
        )

        return response.strip()
