"""DependencyMapper sub-agent — maps module dependencies in code."""

from __future__ import annotations

from typing import Any

from backend.agents.subagents.base_subagent import BaseSubAgent


class DependencyMapper(BaseSubAgent):
    """Maps module dependencies and imports relationships."""

    def __init__(self) -> None:
        super().__init__(
            name="dependency_mapper",
            specialty="mapping module dependencies and import relationships",
        )

    async def map_dependencies(self, code: str) -> dict[str, Any]:
        """Maps module dependencies in code.

        Parameters
        ----------
        code : str
            Source code to analyze.

        Returns
        -------
        dict with keys:
        - modules: list of {name, imports, dependents}
        - circular: list of circular dependency chains
        - suggestions: list of suggestions
        """
        if not code.strip():
            return {"modules": [], "circular": [], "suggestions": []}

        prompt = (
            f"Analyze this code to map module dependencies."
            f"\n\nCode:\n```\n{code[:3000]}\n```\n\n"
            f"Identify:\n"
            f"1. Module imports and dependencies (standard library, 3rd party, local modules)\n"
            f"2. Circular dependencies (if any)\n"
            f"3. Dependency direction and relationships\n"
            f"\nReturn a JSON with:\n"
            f"- modules: array of objects, each with:\n"
            f"  - name: module name\n"
            f"  - imports: array of imported module names\n"
            f"  - dependents: array of modules that depend on this module\n"
            f"- circular: array of circular dependency chains (arrays of module names)\n"
            f"- suggestions: array of suggestions for reducing coupling\n"
            f"\nIf analysis fails, return: INVALID_ANALYSIS\n"
            f"Return only valid JSON, no other text."
        )

        response = await self._call_llm(
            system_prompt="You are a dependency analysis expert. Map module dependencies and identify circular dependencies.",
            user_prompt=prompt,
            max_tokens=1536,
            temperature=0.2,
        )

        if response.strip() == "INVALID_ANALYSIS":
            return {"modules": [], "circular": [], "suggestions": []}

        import json
        try:
            result = json.loads(response)
            # Validate structure
            if isinstance(result, dict) and "modules" in result:
                modules = result.get("modules", [])
                circular = result.get("circular", [])
                suggestions = result.get("suggestions", [])
                return {"modules": modules, "circular": circular, "suggestions": suggestions}
        except (json.JSONDecodeError, TypeError):
            pass

        # Fallback analysis
        return {
            "modules": [],
            "circular": [],
            "suggestions": [
                "Consider refactoring to reduce coupling between modules",
                "Use dependency injection for better testability",
                "Identify and break circular dependencies"
            ]
        }