"""Optimizer sub-agent — suggests and applies performance optimizations."""

from __future__ import annotations

from typing import Any

from backend.agents.subagents.base_subagent import BaseSubAgent


class Optimizer(BaseSubAgent):
    """Suggests performance optimizations and applies them."""

    def __init__(self) -> None:
        super().__init__(
            name="optimizer",
            specialty="suggesting and applying performance optimizations",
        )

    async def suggest_optimization(self, code: str, finding: dict[str, Any]) -> dict[str, Any]:
        """Suggests performance optimization.

        Parameters
        ----------
        code : str
            Source code to optimize.
        finding : dict
            Finding with performance issue details.

        Returns
        -------
        dict with keys: optimization, description, steps, expected_gain.
        """
        if not code.strip():
            return {"optimization": "", "description": "", "steps": [], "expected_gain": ""}

        title = finding.get("title", "") or finding.get("pattern", "")
        location = finding.get("location", "")
        severity = finding.get("severity", "")
        description = finding.get("description", "")

        prompt = (
            f"Suggest a performance optimization for the following finding.\n\n"
            f"Code:\n```\n{code[:2000]}\n```\n\n"
            f"Finding:\n"
            f"Title: {title}\n"
            f"Location: {location}\n"
            f"Severity: {severity}\n"
            f"Description: {description}\n\n"
            f"Provide:\n"
            f"1. Optimization: concise optimization name\n"
            f"2. Description: what optimization to apply and why\n"
            f"3. Steps: array of optimization steps (strings)\n"
            f"4. Expected gain: performance improvement expected\n"
            f"\nReturn as JSON object with these 4 keys."
        )

        response = await self._call_llm(
            system_prompt="You are a performance optimization expert. Suggest efficient optimizations that improve runtime performance.",
            user_prompt=prompt,
            max_tokens=1536,
            temperature=0.2,
        )

        import json
        try:
            result = json.loads(response)
            return {
                "optimization": result.get("optimization", ""),
                "description": result.get("description", ""),
                "steps": result.get("steps", []),
                "expected_gain": result.get("expected_gain", ""),
            }
        except (json.JSONDecodeError, TypeError):
            return {
                "optimization": "Caching",
                "description": f"Add caching based on finding: {title}",
                "steps": [
                    "Identify repeated computations",
                    "Add memoization decorator or cache",
                    "Benchmark before and after"
                ],
                "expected_gain": "2-10x performance improvement for repeated operations"
            }

    async def apply_optimization(self, code: str, optimization: str) -> str:
        """Applies optimization to code.

        Parameters
        ----------
        code : str
            Source code to optimize.
        optimization : str
            Optimization to apply.

        Returns
        -------
        str
            Optimized code.
        """
        if not code.strip() or not optimization.strip():
            return code

        prompt = (
            f"Apply the {optimization} optimization to the following code.\n\n"
            f"Code:\n```\n{code[:2000]}\n```\n\n"
            f"Requirements:\n"
            f"1. Apply the optimization: {optimization}\n"
            f"2. Generate ONLY the optimized code\n"
            f"3. Ensure code still compiles and works correctly\n"
            f"4. No comments about the optimization changes\n"
            f"5. Return code within triple backticks (```)\n"
        )

        response = await self._call_llm(
            system_prompt="You are a performance optimization specialist. Apply optimizations cleanly without breaking functionality.",
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
