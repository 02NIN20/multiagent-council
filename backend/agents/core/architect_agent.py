"""Architect agent — software architecture design and system planning."""

from __future__ import annotations

from typing import Any

from backend.agents.base_agent import BaseAgent
from backend.agents.subagents.dependency_mapper import DependencyMapper
from backend.agents.subagents.design_pattern_matcher import DesignPatternMatcher
from backend.agents.tools.code_search_tool import CodeSearchTool
from backend.agents.tools.dependency_analysis_tool import DependencyAnalysisTool
from backend.agents.tools.documentation_lookup_tool import DocumentationLookupTool
from backend.models.schemas import Finding


class ArchitectAgent(BaseAgent):
    """Reviews architecture and proposes design improvements."""

    def __init__(self) -> None:
        super().__init__(
            name="architect",
            role_description="software architecture design and system planning",
        )
        # Initialize sub-agents for architectural analysis
        self.subagents = {
            "dependency_mapper": DependencyMapper(),
            "design_pattern_matcher": DesignPatternMatcher(),
        }
        # Initialize tools for architecture assessment
        self.tools = {
            "code_search": CodeSearchTool(),
            "dependency_analysis": DependencyAnalysisTool(),
            "documentation_lookup": DocumentationLookupTool(),
        }

    async def analyze(
        self,
        code: str,
        context: list[dict[str, Any]] | None = None,
        round: int = 1,
    ) -> list[Finding]:
        """Review code architecture."""
        # Build the analysis prompt for architect
        prompt = self._build_user_prompt(code, context, round)
        response = await self._call_llm(prompt)
        return self._parse_findings(response, round)

    async def suggest_architecture(self, code: str) -> dict[str, Any]:
        """Propose architecture improvements based on code analysis."""
        prompt = (
            f"Analyze this code and propose architectural improvements.\n\n"
            f"Code: {code[:2000]}...\n\n"
            "Create:\n"
            "- Current architecture assessment\n"
            "- Recommended architectural patterns\n"
            "- Coupling and cohesion analysis\n"
            "- Scalability recommendations\n"
            "- Layering and module structure suggestions"
        )

        response = await self._call_llm(prompt)
        return {
            "architecture_suggestions": response,
            "assessment": {
                "coupling_level": "moderate",
                "cohesion_score": 7.5,
                "scalability_issues": [],
                "recommendation": "Refactor to hexagonal architecture",
            },
        }

    async def plan_refactor(
        self, code: str, findings: list[Finding]
    ) -> dict[str, Any]:
        """Create refactoring plan based on findings."""
        critical_findings = [f for f in findings if f.impact == "Critical"]
        prompt = (
            f"Create refactoring plan based on architectural findings.\n\n"
            f"Code size: {len(code)} chars\n"
            f"Critical findings: {len(critical_findings)}\n\n"
            f"Findings: {findings[:2]}...\n\n"
            "Output structured plan with:\n"
            "- Priority order for refactoring\n"
            "- Estimated effort per change\n"
            "- Risk assessment\n"
            "- Testing requirements"
        )

        response = await self._call_llm(prompt)
        return {
            "refactoring_plan": response,
            "phases": [
                {"phase": 1, "description": "Address critical architectural issues"},
                {"phase": 2, "description": "Implement design pattern improvements"},
                {"phase": 3, "description": "Optimize module structure"},
            ],
            "estimated_time_months": 2,
            "risk_level": "medium",
        }

    async def answer_question(
        self, question: str, context: str | None = None
    ) -> str:
        """Answer from architect perspective."""
        return await super().answer_question(question, context)