"""StaticAnalyzer sub-agent — performs static code analysis."""

from __future__ import annotations

from typing import Any

from backend.agents.subagents.base_subagent import BaseSubAgent


class StaticAnalyzer(BaseSubAgent):
    """Performs static analysis: linting, style checks, basic error detection."""

    def __init__(self) -> None:
        super().__init__(
            name="static_analyzer",
            specialty="static code analysis, linting, and style verification",
        )

    async def analyze_static(self, code: str) -> list[dict[str, Any]]:
        """Run static analysis on code.

        Parameters
        ----------
        code : str
            Source code to analyse.

        Returns
        -------
        list of issue dicts with keys: line, issue, severity.
        """
        if not code.strip():
            return []

        prompt = (
            f"Perform a static code analysis on the following code. "
            f"Identify syntax issues, style violations, unused variables, "
            f"missing imports, and potential bugs.\n\n"
            f"Code:\n```\n{code[:3000]}\n```\n\n"
            f"For each issue, return: LINE, ISSUE, SEVERITY (Critical/High/Medium/Low)\n"
            f"If no issues, return: NO_ISSUES"
        )

        response = await self._call_llm(
            system_prompt="You are a static code analysis tool. Find syntax, style, and logic issues.",
            user_prompt=prompt,
            max_tokens=1536,
            temperature=0.1,
        )

        if response.strip() == "NO_ISSUES":
            return []

        issues = []
        for block in response.strip().split("\n\n"):
            lines = block.strip().split("\n")
            issue = {}
            for line in lines:
                if line.startswith("LINE:"):
                    issue["line"] = line[5:].strip()
                elif line.startswith("ISSUE:"):
                    issue["issue"] = line[6:].strip()
                elif line.startswith("SEVERITY:"):
                    issue["severity"] = line[9:].strip()
            if issue:
                issues.append(issue)
        return issues
