"""Tool for basic static code analysis — complexity, style issues, etc."""

from __future__ import annotations

import re
from typing import Any

from backend.agents.tools.base_tool import BaseTool


class StaticAnalysisTool(BaseTool):
    """Perform basic static analysis: cyclomatic complexity, line count, nesting depth."""

    def __init__(self) -> None:
        super().__init__(
            name="static_analysis",
            description="Analyse code complexity, nesting depth, function length, and style issues.",
        )

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """Execute static analysis.

        Parameters
        ----------
        code : str
            Source code to analyse.
        analysis_type : str
            'complexity', 'nesting', 'length', 'style', or 'all'

        Returns
        -------
        dict with analysis results.
        """
        code: str = kwargs.get("code", "")
        analysis_type: str = kwargs.get("analysis_type", "all")

        if not code:
            return {"error": "No code provided"}

        lines = code.split("\n")
        results: dict[str, Any] = {
            "total_lines": len(lines),
            "code_lines": sum(1 for l in lines if l.strip() and not l.strip().startswith("#")),
            "blank_lines": sum(1 for l in lines if not l.strip()),
        }

        if analysis_type in ("complexity", "all"):
            # Estimate cyclomatic complexity by counting decision points
            decisions = len(re.findall(
                r"\b(if|elif|else|for|while|and|or|not|except|with|assert)\b",
                code,
            ))
            results["estimated_cyclomatic_complexity"] = max(1, decisions)

        if analysis_type in ("nesting", "all"):
            # Estimate max nesting depth
            max_depth = 0
            current_depth = 0
            for line in lines:
                stripped = line.strip()
                if stripped.startswith(("if ", "elif ", "else:", "for ", "while ", "with ", "try:", "except ", "def ", "class ")):
                    indent = len(line) - len(line.lstrip())
                    depth = indent // 4  # assume 4-space indent
                    current_depth = depth + 1
                    max_depth = max(max_depth, current_depth)
            results["max_nesting_depth"] = max_depth

        if analysis_type in ("length", "all"):
            # Find long functions
            long_functions = []
            func_pattern = re.compile(r"^\s*(async\s+)?def\s+\w+")
            in_function = False
            func_start = 0
            func_name = ""
            for i, line in enumerate(lines, 1):
                if func_pattern.search(line):
                    if in_function:
                        length = i - func_start
                        if length > 50:  # threshold
                            long_functions.append({"name": func_name, "start_line": func_start, "length": length})
                    func_name = line.strip().split("def ")[-1].split("(")[0]
                    func_start = i
                    in_function = True
            if in_function:
                length = len(lines) - func_start
                if length > 50:
                    long_functions.append({"name": func_name, "start_line": func_start, "length": length})
            results["long_functions"] = long_functions

        if analysis_type in ("style", "all"):
            # Check for common style issues
            style_issues = []
            # Lines > 100 chars
            for i, line in enumerate(lines, 1):
                if len(line) > 100 and not line.strip().startswith("#"):
                    style_issues.append({"line": i, "issue": "line too long (>100 chars)", "text": line[:80]})
            # Missing docstrings
            for i, line in enumerate(lines, 1):
                if re.match(r"^\s*(async\s+)?def\s+\w+\s*\(", line):
                    # Check next non-blank line for docstring
                    for j in range(i, min(i + 3, len(lines))):
                        next_line = lines[j].strip()
                        if next_line.startswith(('"""', "'''", '"')):
                            break
                    else:
                        style_issues.append({"line": i, "issue": f"missing docstring in function", "text": line.strip()[:60]})
            results["style_issues"] = style_issues

        return results
