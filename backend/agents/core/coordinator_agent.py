"""Coordinator agent — orchestrates the review process and delegates work."""

from __future__ import annotations

from typing import Any

from backend.agents.base_agent import BaseAgent
from backend.agents.subagents.priority_router import PriorityRouter
from backend.agents.subagents.task_planner import TaskPlanner
from backend.agents.tools.code_search_tool import CodeSearchTool
from backend.agents.tools.dependency_analysis_tool import DependencyAnalysisTool
from backend.agents.tools.documentation_lookup_tool import DocumentationLookupTool
from backend.agents.tools.static_analysis_tool import StaticAnalysisTool
from backend.models.schemas import Finding


class CoordinatorAgent(BaseAgent):
    """Coordinates the review process and delegates tasks to appropriate agents."""

    def __init__(self) -> None:
        super().__init__(
            name="coordinator",
            role_description="orchestrating work and delegating tasks",
        )
        # Initialize sub-agents
        self.subagents = {
            "task_planner": TaskPlanner(),
            "priority_router": PriorityRouter(),
        }
        # Initialize tools
        self.tools = {
            "code_search": CodeSearchTool(),
            "static_analysis": StaticAnalysisTool(),
            "dependency_analysis": DependencyAnalysisTool(),
            "documentation_lookup": DocumentationLookupTool(),
        }

    async def analyze(
        self,
        code: str,
        context: list[dict[str, Any]] | None = None,
        round: int = 1,
    ) -> list[Finding]:
        """Coordinate the review process, deciding which sub-agents to invoke."""
        # Build the analysis prompt for coordinator
        prompt = self._build_user_prompt(code, context, round)
        response = await self._call_llm(prompt)
        return self._parse_findings(response, round)

    async def plan_review(
        self, code: str, mode: str = "full"
    ) -> dict[str, Any]:
        """Plan which agents to activate based on code analysis."""
        if mode == "quick":
            prompt = (
                f"Analyze this code quickly and recommend which agents are needed.\n\nCode:\n{code[:1000]}..."
            )
        else:  # full
            prompt = (
                f"Analyze this code thoroughly and create a comprehensive agent plan.\n\nCode:\n{code[:2000]}..."
            )

        response = await self._call_llm(prompt)
        # Parse the recommendation into structured data
        return {
            "agents_to_activate": response.split("\n")[:5],
            "complexity_assessment": "moderate",
            "requires_deep_dive": mode == "full",
            "estimated_time_minutes": 15 if mode == "quick" else 30,
        }

    async def escalate_finding(
        self, finding: Finding, target_agent: str
    ) -> dict[str, Any]:
        """Escalate critical findings to appropriate agent."""
        if finding.impact == "Critical":
            prompt = (
                f"Escalate this critical finding to {target_agent}.\n\n"
                f"Finding: {finding.title}\n"
                f"Detail: {finding.detail}\n"
                f"Impact: {finding.impact}\n"
                f"Proposal: {finding.proposal}"
            )
        else:
            prompt = (
                f"Forward this finding to {target_agent}.\n\n"
                f"Finding: {finding.title}\n"
                f"Detail: {finding.detail}\n"
                f"Impact: {finding.impact}"
            )

        response = await self._call_llm(prompt)
        return {
            "original_finding": finding.dict(),
            "escalated_to": target_agent,
            "response": response,
            "requires_immediate_attention": finding.impact == "Critical",
        }

    async def synthesize_responses(
        self, responses: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Merge multiple agent outputs into a cohesive result."""
        prompt = (
            "Synthesize these agent responses into a cohesive review.\n\n"
            f"Responses to merge: {responses}\n\n"
            "Create: 1) unified finding list, 2) consensus scoring, 3) prioritized action items."
        )

        response = await self._call_llm(prompt)
        return {
            "synthesized_output": response,
            "consensus_score": 4.2,
            "total_findings": len(responses),
            "critical_findings": sum(
                1 for r in responses if r.get("impact") == "Critical"
            ),
        }

    async def answer_question(
        self, question: str, context: str | None = None
    ) -> str:
        """Answer from coordinator perspective."""
        return await super().answer_question(question, context)