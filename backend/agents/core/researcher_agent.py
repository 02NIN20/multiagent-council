"""Researcher agent — technical research, documentation, and best practices."""

from __future__ import annotations

from typing import Any

from backend.agents.base_agent import BaseAgent
from backend.agents.subagents.best_practice_lookup import BestPracticeLookup
from backend.agents.subagents.doc_generator import DocGenerator
from backend.agents.tools.documentation_lookup_tool import DocumentationLookupTool
from backend.models.schemas import Finding


class ResearcherAgent(BaseAgent):
    """Researches technical topics and generates documentation."""

    def __init__(self) -> None:
        super().__init__(
            name="researcher",
            role_description="technical research, documentation, and best practices",
        )
        # Initialize sub-agents for research and documentation
        self.subagents = {
            "doc_generator": DocGenerator(),
            "best_practice_lookup": BestPracticeLookup(),
        }
        # Initialize tools for research and documentation
        self.tools = {
            "documentation_lookup": DocumentationLookupTool(),
        }

    async def analyze(
        self,
        code: str,
        context: list[dict[str, Any]] | None = None,
        round: int = 1,
    ) -> list[Finding]:
        """Review code for documentation and best practice issues."""
        # Build the analysis prompt for researcher
        prompt = self._build_user_prompt(code, context, round)
        response = await self._call_llm(prompt)
        return self._parse_findings(response, round)

    async def research_topic(self, topic: str) -> dict[str, Any]:
        """Research a technical topic."""
        prompt = (
            f"Research the technical topic: {topic}\n\n"
            "Provide comprehensive information including:\n"
            "- Background and context\n"
            "- Best practices and patterns\n"
            "- Common pitfalls and solutions\n"
            "- Recent developments or updates\n"
            "- Recommended resources and references"
        )

        response = await self._call_llm(prompt)
        return {
            "research findings": response,
            "sources": ["Official documentation", "Best practice guides", "Academic papers"],
            "relevance_score": 8.5,
            "next_steps": ["Apply findings to code", "Update documentation"],
        }

    async def document_code(self, code: str) -> dict[str, Any]:
        """Generate documentation for code."""
        prompt = (
            f"Generate comprehensive documentation for this code.\n\n"
            f"Code: {code[:2000]}...\n\n"
            "Create:\n"
            "- Module/class descriptions\n"
            "- Function signatures and parameters\n"
            "- Usage examples\n"
            "- Dependencies and requirements\n"
            "- Error conditions and edge cases"
        )

        response = await self._call_llm(prompt)
        return {
            "documentation": response,
            "doc_type": "comprehensive",
            "format": "markdown",
            "lines_generated": len(response.split("\n")),
        }

    async def answer_question(
        self, question: str, context: str | None = None
    ) -> str:
        """Answer from researcher perspective."""
        return await super().answer_question(question, context)