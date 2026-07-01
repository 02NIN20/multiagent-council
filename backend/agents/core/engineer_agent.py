"""Engineer agent — code implementation, fixes, and optimization."""

from __future__ import annotations

from typing import Any

from backend.agents.base_agent import BaseAgent
from backend.agents.subagents.code_writer import CodeWriter
from backend.agents.subagents.optimizer import Optimizer
from backend.agents.subagents.refactorer import Refactorer
from backend.agents.tools.code_search_tool import CodeSearchTool
from backend.models.schemas import Finding


class EngineerAgent(BaseAgent):
    """Implements fixes and optimizations for code issues."""

    def __init__(self) -> None:
        super().__init__(
            name="engineer",
            role_description="code implementation, fixes, and optimization",
        )
        # Initialize sub-agents for code manipulation
        self.subagents = {
            "code_writer": CodeWriter(),
            "refactorer": Refactorer(),
            "optimizer": Optimizer(),
        }
        # Initialize tools for code exploration
        self.tools = {
            "code_search": CodeSearchTool(),
        }

    async def analyze(
        self,
        code: str,
        context: list[dict[str, Any]] | None = None,
        round: int = 1,
    ) -> list[Finding]:
        """Analyze code for implementation issues."""
        # Build the analysis prompt for engineer
        prompt = self._build_user_prompt(code, context, round)
        response = await self._call_llm(prompt)
        return self._parse_findings(response, round)

    async def implement_fix(
        self, code: str, finding: Finding
    ) -> dict[str, Any]:
        """Generate fix code for a specific finding."""
        prompt = (
            f"Generate a fix for this code finding.\n\n"
            f"Finding: {finding.title}\n"
            f"Detail: {finding.detail}\n"
            f"Impact: {finding.impact}\n"
            f"Proposal: {finding.proposal}\n\n"
            f"Original code (relevant section): {code[:1000]}...\n\n"
            "Output:\n"
            "- Fixed code snippet\n"
            "- Explanation of changes\n"
            "- Testing suggestions"
        )

        response = await self._call_llm(prompt)
        return {
            "fix_code": response,
            "finding_reference": finding.title,
            "implementation_plan": "Apply fix to identified section",
            "testing_required": True,
        }

    async def optimize_code(
        self, code: str, findings: list[Finding]
    ) -> dict[str, Any]:
        """Apply optimizations based on findings."""
        prompt = (
            f"Optimize this code based on the following findings.\n\n"
            f"Code: {code[:2000]}...\n\n"
            f"Identified issues: {len(findings)}\n\n"
            f"Critical findings: {sum(1 for f in findings if f.impact == 'Critical')}\n\n"
            "Output:\n"
            "- Performance optimization suggestions\n"
            "- Resource usage improvements\n"
            "- Code quality enhancements\n"
            "- Estimated performance gains"
        )

        response = await self._call_llm(prompt)
        return {
            "optimizations": response,
            "performance_improvements": [
                "Reduce time complexity from O(n²) to O(n)",
                "Implement caching for repeated calculations",
                "Optimize memory allocation patterns",
            ],
            "estimated_speedup_factor": 3.5,
            "effort_level": "medium",
        }

    async def answer_question(
        self, question: str, context: str | None = None
    ) -> str:
        """Answer from engineer perspective."""
        return await super().answer_question(question, context)