"""StyleChecker sub-agent — checks code for style violations."""

from __future__ import annotations

from typing import Any

from backend.agents.subagents.base_subagent import BaseSubAgent


class StyleChecker(BaseSubAgent):
    """Checks code for style violations and best practice deviations."""

    def __init__(self) -> None:
        super().__init__(
            name="style_checker",
            specialty="checking code for style violations and best practice deviations",
        )

    async def check_style(self, code: str) -> list[dict[str, Any]]:
        """Checks code style.

        Parameters
        ----------
        code : str
            Source code to check.

        Returns
        -------
        list of issue dicts with keys: issue, line, severity, suggestion.
        """
        if not code.strip():
            return []

        prompt = (
            f"Check this code for style violations and best practice deviations.\n\n"
            f"Code:\n```\n{code[:3000]}\n```\n\n"
            f"Check for style issues including:\n"
            f"1. Line length (should be < 100 chars)\n"
            f"2. Naming conventions (snake_case for variables/functions)\n"
            f"3. Import ordering (standard library, then 3rd party, then local)\n"
            f"4. Use of trailing commas in collections\n"
            f"5. Docstring format and presence\n"
            f"6. Type hints usage\n"
            f"7. Magic numbers (use constants instead)\n"
            f"8. Unused imports\n"
            f"9. Code formatting (indentation, spacing)\n"
            f"10. Consistent use of quotes (double vs single)\n\n"
            f"For each issue, return:\n"
            f"ISSUE: <description of style problem>\n"
            f"LINE: <line number where issue occurs>\n"
            f"SEVERITY: <Critical|High|Medium|Low>\n"
            f"SUGGESTION: <how to fix the style issue>\n\n"
            f"If no issues found, return: NO_STYLE_ISSUES\n"
            f"Separate each issue with '---' separator."
        )

        response = await self._call_llm(
            system_prompt="You are a style expert. Check code against PEP 8 and best practices for Python code quality.",
            user_prompt=prompt,
            max_tokens=2048,
            temperature=0.1,
        )

        if response.strip() == "NO_STYLE_ISSUES":
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
                elif line.startswith("LINE:"):
                    issue["line"] = line[5:].strip()
                elif line.startswith("SEVERITY:"):
                    issue["severity"] = line[9:].strip()
                elif line.startswith("SUGGESTION:"):
                    issue["suggestion"] = line[11:].strip()
            if issue.get("issue"):
                issues.append(issue)
        return issues
