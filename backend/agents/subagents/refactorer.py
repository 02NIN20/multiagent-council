"""Refactorer sub-agent — suggests and applies refactoring strategies."""

from __future__ import annotations

from typing import Any

from backend.agents.subagents.base_subagent import BaseSubAgent


class Refactorer(BaseSubAgent):
    """Suggests and applies refactoring to code."""

    def __init__(self) -> None:
        super().__init__(
            name="refactorer",
            specialty="suggesting and applying refactoring strategies",
        )

    async def suggest_refactoring(self, code: str, finding: dict[str, Any]) -> dict[str, Any]:
        """Suggests refactoring strategy.

        Parameters
        ----------
        code : str
            Source code to refactor.
        finding : dict
            Finding with issue details.

        Returns
        -------
        dict with keys: strategy, description, steps, impact.
        """
        if not code.strip():
            return {"strategy": "", "description": "", "steps": [], "impact": ""}

        title = finding.get("title", "") or finding.get("pattern", "")
        location = finding.get("location", "")
        severity = finding.get("severity", "")
        description = finding.get("description", "")
        proposal = finding.get("proposal", "")

        prompt = (
            f"Suggest a refactoring strategy for the following finding.\n\n"
            f"Code:\n```\n{code[:2000]}\n```\n\n"
            f"Finding:\n"
            f"Title: {title}\n"
            f"Location: {location}\n"
            f"Severity: {severity}\n"
            f"Description: {description}\n"
            f"Current Proposal: {proposal}\n\n"
            f"Provide:\n"
            f"1. Strategy: concise refactoring approach name\n"
            f"2. Description: detailed explanation of what will be refactored\n"
            f"3. Steps: array of refactoring steps (strings)\n"
            f"4. Impact: expected impact on code quality and performance\n"
            f"\nReturn as JSON object with these 4 keys."
        )

        response = await self._call_llm(
            system_prompt="You are a refactoring expert. Suggest strategic refactoring approaches that improve code structure and maintainability.",
            user_prompt=prompt,
            max_tokens=1536,
            temperature=0.2,
        )

        import json
        try:
            result = json.loads(response)
            return {
                "strategy": result.get("strategy", ""),
                "description": result.get("description", ""),
                "steps": result.get("steps", []),
                "impact": result.get("impact", ""),
            }
        except (json.JSONDecodeError, TypeError):
            return {
                "strategy": "Extract Method",
                "description": f"Refactor based on finding: {title}",
                "steps": [
                    f"Extract problematic code at {location} into a separate method",
                    "Update references to use the new method",
                    "Add appropriate documentation"
                ],
                "impact": "Improved readability and testability"
            }

    async def apply_refactoring(self, code: str, strategy: str) -> str:
        """Applies refactoring to code.

        Parameters
        ----------
        code : str
            Source code to refactor.
        strategy : str
            Refactoring strategy to apply.

        Returns
        -------
        str
            Refactored code.
        """
        if not code.strip() or not strategy.strip():
            return code

        prompt = (
            f"Apply the {strategy} refactoring to the following code.\n\n"
            f"Code:\n```\n{code[:2000]}\n```\n\n"
            f"Requirements:\n"
            f"1. Apply the refactoring strategy: {strategy}\n"
            f"2. Generate ONLY the refactored code\n"
            f"3. Ensure code still compiles and works correctly\n"
            f"4. No comments about the refactoring changes\n"
            f"5. Return code within triple backticks (```)\n"
        )

        response = await self._call_llm(
            system_prompt="You are an expert refactoring specialist. Apply refactoring strategies cleanly without breaking functionality.",
            user_prompt=prompt,
            max_tokens=2048,
            temperature=0.1,
        )

        # Extract code from backticks
        if "```" in response:
            code_blocks = response.split("```")
            if len(code_blocks) >= 2:
                return code_blocks[1].strip()

        return response.strip()
