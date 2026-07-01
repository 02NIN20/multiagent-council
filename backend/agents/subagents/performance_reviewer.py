"""PerformanceReviewer sub-agent — reviews code for performance issues."""

from __future__ import annotations

from typing import Any

from backend.agents.subagents.base_subagent import BaseSubAgent


class PerformanceReviewer(BaseSubAgent):
    """Reviews code for performance issues and bottlenecks."""

    def __init__(self) -> None:
        super().__init__(
            name="performance_reviewer",
            specialty="reviewing code for performance issues and bottlenecks",
        )

    async def review_performance(self, code: str) -> list[dict[str, Any]]:
        """Reviews code for performance issues.

        Parameters
        ----------
        code : str
            Source code to review.

        Returns
        -------
        list of issue dicts with keys: issue, severity, location, optimization.
        """
        if not code.strip():
            return []

        prompt = (
            f"Review this code for performance issues and bottlenecks.\n\n"
            f"Code:\n```\n{code[:3000]}\n```\n\n"
            f"Identify performance issues including:\n"
            f"1. N+1 query problems (for database access)\n"
            f"2. Inefficient loops and iterations\n"
            f"3. Unnecessary memory allocations\n"
            f"4. Blocking I/O operations in async code\n"
            f"5. Inefficient string operations\n"
            f"6. Missing caching opportunities\n"
            f"7. Inefficient data structures\n"
            f"8. CPU-intensive operations in hot paths\n"
            f"9. Serialization/deserialization overhead\n"
            f"10. Unused or redundant code\n\n"
            f"For each issue, return:\n"
            f"ISSUE: <description of performance problem>\n"
            f"SEVERITY: <Critical|High|Medium|Low>\n"
            f"LOCATION: <where the issue occurs in code>\n"
            f"OPTIMIZATION: <suggested optimization approach>\n\n"
            f"If no issues found, return: NO_PERFORMANCE_ISSUES\n"
            f"Separate each issue with '---' separator."
        )

        response = await self._call_llm(
            system_prompt="You are a performance expert. Review code for performance issues, bottlenecks, and inefficiencies.",
            user_prompt=prompt,
            max_tokens=2048,
            temperature=0.1,
        )

        if response.strip() == "NO_PERFORMANCE_ISSUES":
            return []

        issues = []
        blocks = response.strip().split("---")
        for block in blocks:
            if not block.strip():
                continue
            issue = {}
            lines = block.strip().split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("ISSUE:"):
                    issue["issue"] = line[6:].strip()
                elif line.startswith("SEVERITY:"):
                    issue["severity"] = line[9:].strip()
                elif line.startswith("LOCATION:"):
                    issue["location"] = line[9:].strip()
                elif line.startswith("OPTIMIZATION:"):
                    issue["optimization"] = line[12:].strip()
            if issue.get("issue"):
                issues.append(issue)
        return issues
