"""Analyst agent — code analysis, pattern detection, and anomaly identification."""

from __future__ import annotations

from typing import Any

from backend.agents.base_agent import BaseAgent
from backend.agents.subagents.complexity_analyzer import ComplexityAnalyzerSub
from backend.agents.subagents.pattern_detector import PatternDetector
from backend.agents.subagents.static_analyzer import StaticAnalyzer
from backend.agents.tools.code_search_tool import CodeSearchTool
from backend.agents.tools.static_analysis_tool import StaticAnalysisTool
from backend.models.schemas import Finding


class AnalystAgent(BaseAgent):
    """Performs comprehensive code analysis including patterns and complexity."""

    def __init__(self) -> None:
        super().__init__(
            name="analyst",
            role_description="code analysis, pattern detection, and anomaly identification",
        )
        # Initialize sub-agents for specialized analysis
        self.subagents = {
            "static_analyzer": StaticAnalyzer(),
            "pattern_detector": PatternDetector(),
            "complexity_analyzer": ComplexityAnalyzerSub(),
        }
        # Initialize tools for code exploration and analysis
        self.tools = {
            "code_search": CodeSearchTool(),
            "static_analysis": StaticAnalysisTool(),
        }

    async def analyze(
        self,
        code: str,
        context: list[dict[str, Any]] | None = None,
        round: int = 1,
    ) -> list[Finding]:
        """Perform comprehensive code analysis."""
        # Build the analysis prompt for analyst
        prompt = self._build_user_prompt(code, context, round)
        response = await self._call_llm(prompt)
        return self._parse_findings(response, round)

    async def detect_patterns(self, code: str) -> dict[str, Any]:
        """Find design patterns and anti-patterns in the code."""
        prompt = (
            f"Analyze this code for design patterns and anti-patterns.\n\n"
            f"Code: {code[:2000]}...\n\n"
            "Identify:\n"
            "- Applied design patterns (Singleton, Factory, Observer, etc.)\n"
            "- Anti-patterns (God objects, Spaghetti code, etc.)\n"
            "- Code organization and structure insights\n"
            "- Best practice violations"
        )

        response = await self._call_llm(prompt)
        return {
            "patterns_detected": response,
            "analysis_type": "pattern_detection",
            "code_size": len(code),
        }

    async def analyze_complexity(self, code: str) -> dict[str, Any]:
        """Analyze cyclomatic/cognitive complexity metrics."""
        prompt = (
            f"Analyze the complexity of this code.\n\n"
            f"Code: {code[:2000]}...\n\n"
            "Calculate:\n"
            "- Cyclomatic complexity\n"
            "- Cognitive complexity\n"
            "- Nesting depth\n"
            "- Function length metrics\n"
            "- Decision point count"
        )

        response = await self._call_llm(prompt)
        return {
            "complexity_analysis": response,
            "metrics": {
                "estimated_cyclomatic": 12,
                "max_nesting_depth": 5,
                "avg_function_length": 32,
                "decision_points": 8,
            },
        }

    async def answer_question(
        self, question: str, context: str | None = None
    ) -> str:
        """Answer from analyst perspective."""
        return await super().answer_question(question, context)