"""ComplexityAnalyzer sub-agent — analyses code complexity."""

from __future__ import annotations

from typing import Any
from backend.agents.subagents.base_subagent import BaseSubAgent


class ComplexityAnalyzerSub(BaseSubAgent):
    """Analyses cyclomatic and cognitive complexity."""

    def __init__(self) -> None:
        super().__init__(name="complexity_analyzer", specialty="analysing code complexity metrics")

    async def analyze_complexity(self, code: str) -> dict[str, Any]:
        if not code.strip():
            return {"cyclomatic_complexity": 0, "cognitive_complexity": 0, "hotspots": []}
        prompt = (
            f"Analyse the complexity of this code.\n\nCode:\n```\n{code[:3000]}\n```\n\n"
            f"Return: CYCLOMATIC_COMPLEXITY: <score>, COGNITIVE_COMPLEXITY: <score>, "
            f"HOTSPOTS: <list of complex functions with line numbers>\n"
            f"Return NA if not applicable."
        )
        response = await self._call_llm(
            system_prompt="You are a code complexity analyst. Provide accurate complexity metrics.",
            user_prompt=prompt, max_tokens=1024, temperature=0.1,
        )
        lines = response.strip().split("\n")
        result = {"cyclomatic_complexity": 0, "cognitive_complexity": 0, "hotspots": []}
        for line in lines:
            if "CYCLOMATIC_COMPLEXITY:" in line:
                val = line.split(":")[-1].strip()
                try: result["cyclomatic_complexity"] = int(val)
                except: pass
            elif "COGNITIVE_COMPLEXITY:" in line:
                val = line.split(":")[-1].strip()
                try: result["cognitive_complexity"] = int(val)
                except: pass
            elif "HOTSPOTS:" in line:
                hotspots = line.split(":")[-1].strip()
                if hotspots and hotspots != "NA":
                    result["hotspots"] = [h.strip() for h in hotspots.split(",")]
        return result
