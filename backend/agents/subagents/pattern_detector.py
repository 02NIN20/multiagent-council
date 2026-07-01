"""PatternDetector sub-agent — detects design patterns and anti-patterns."""

from __future__ import annotations

from typing import Any

from backend.agents.subagents.base_subagent import BaseSubAgent


class PatternDetector(BaseSubAgent):
    """Detects design patterns, anti-patterns, and code smells."""

    def __init__(self) -> None:
        super().__init__(
            name="pattern_detector",
            specialty="detecting design patterns, anti-patterns, and code smells",
        )

    async def detect_patterns(self, code: str) -> list[dict[str, Any]]:
        """Detect design patterns and anti-patterns in code.

        Parameters
        ----------
        code : str
            Source code to analyse.

        Returns
        -------
        list of pattern dicts with keys: type, pattern, description, location.
        """
        if not code.strip():
            return []

        prompt = (
            f"Analyse this code for design patterns and anti-patterns.\n\n"
            f"Code:\n```\n{code[:3000]}\n```\n\n"
            f"Identify:\n"
            f"1. Design patterns in use (Singleton, Factory, Observer, etc.)\n"
            f"2. Anti-patterns (God Object, Spaghetti Code, Golden Hammer, etc.)\n"
            f"3. Code smells (long methods, large classes, feature envy, etc.)\n\n"
            f"For each, return:\n"
            f"TYPE: pattern | anti-pattern | code-smell\n"
            f"PATTERN: <name>\n"
            f"DESCRIPTION: <brief description>\n"
            f"LOCATION: <where in the code>\n\n"
            f"If none found, return: NO_PATTERNS"
        )

        response = await self._call_llm(
            system_prompt="You are a design pattern expert. Identify patterns, anti-patterns, and code smells.",
            user_prompt=prompt,
            max_tokens=1536,
            temperature=0.2,
        )

        if response.strip() == "NO_PATTERNS":
            return []

        patterns = []
        for block in response.strip().split("\n\n"):
            lines = block.strip().split("\n")
            pattern = {}
            for line in lines:
                if line.startswith("TYPE:"):
                    pattern["type"] = line[5:].strip()
                elif line.startswith("PATTERN:"):
                    pattern["pattern"] = line[8:].strip()
                elif line.startswith("DESCRIPTION:"):
                    pattern["description"] = line[12:].strip()
                elif line.startswith("LOCATION:"):
                    pattern["location"] = line[9:].strip()
            if pattern:
                patterns.append(pattern)
        return patterns
