"""DesignPatternMatcher sub-agent — identifies design patterns in code."""

from __future__ import annotations

from typing import Any

from backend.agents.subagents.base_subagent import BaseSubAgent


class DesignPatternMatcher(BaseSubAgent):
    """Identifies design patterns being used in code."""

    def __init__(self) -> None:
        super().__init__(
            name="design_pattern_matcher",
            specialty="identifying design patterns in source code",
        )

    async def match_patterns(self, code: str) -> list[dict[str, Any]]:
        """Identifies design patterns being used (Singleton, Factory, MVC, Observer, etc.).

        Parameters
        ----------
        code : str
            Source code to analyze.

        Returns
        -------
        list of dict with keys: pattern, confidence, location, reason.
        """
        if not code.strip():
            return []

        prompt = (
            f"Analyze this code to identify design patterns being used."
            f"\n\nCode:\n```\n{code[:3000]}\n```\n\n"
            f"Look for patterns such as:\n"
            f"- Singleton pattern (single instance creation)\n"
            f"- Factory pattern (object creation abstraction)\n"
            f"- MVC pattern (Model-View-Controller separation)\n"
            f"- Observer pattern (observer/subscriber relationship)\n"
            f"- Strategy pattern (algorithm selection)\n"
            f"- Decorator pattern (behavior extension)\n"
            f"- Adapter pattern (interface compatibility)\n"
            f"- Proxy pattern (controlled access)\n"
            f"- Command pattern (request encapsulation)\n"
            f"- Iterator pattern (sequential access)\n"
            f"\nFor each pattern found, return:\n"
            f"PATTERN: <pattern name>\n"
            f"CONFIDENCE: <0-100 score>\n"
            f"LOCATION: <code location or 'multiple'>\n"
            f"REASON: <why this pattern matches>\n\n"
            f"If no patterns found, return: NO_PATTERNS\n"
            f"Separate each pattern with '---' separator."
        )

        response = await self._call_llm(
            system_prompt="You are a design pattern expert. Identify patterns in code with confidence scores.",
            user_prompt=prompt,
            max_tokens=1536,
            temperature=0.2,
        )

        if response.strip() == "NO_PATTERNS":
            return []

        patterns = []
        blocks = response.strip().split("---")
        for block in blocks:
            if not block.strip():
                continue
            pattern = {}
            lines = block.strip().split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("PATTERN:"):
                    pattern["pattern"] = line[8:].strip()
                elif line.startswith("CONFIDENCE:"):
                    try:
                        pattern["confidence"] = int(line[11:].strip())
                    except ValueError:
                        pattern["confidence"] = 50
                elif line.startswith("LOCATION:"):
                    pattern["location"] = line[9:].strip()
                elif line.startswith("REASON:"):
                    pattern["reason"] = line[7:].strip()
            if pattern.get("pattern"):
                patterns.append(pattern)
        return patterns