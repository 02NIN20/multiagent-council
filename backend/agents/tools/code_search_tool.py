"""Tool to search code for patterns, keywords, and structures."""

from __future__ import annotations

import re
from typing import Any

from backend.agents.tools.base_tool import BaseTool


class CodeSearchTool(BaseTool):
    """Search source code for regex patterns, function definitions, imports, etc."""

    def __init__(self) -> None:
        super().__init__(
            name="code_search",
            description="Search source code for regex patterns, function/class definitions, and imports.",
        )

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """Execute code search.

        Parameters
        ----------
        code : str
            Source code to search in.
        pattern : str
            Regex pattern to search for.
        search_type : str, optional
            Type of search: 'regex', 'function', 'class', 'import', 'comment'

        Returns
        -------
        dict with keys: matches (list of {line, text}), count (int)
        """
        code: str = kwargs.get("code", "")
        pattern: str = kwargs.get("pattern", "")
        search_type: str = kwargs.get("search_type", "regex")

        if not code:
            return {"matches": [], "count": 0}

        lines = code.split("\n")
        matches = []

        if search_type == "function":
            func_pattern = re.compile(r"^\s*(async\s+)?def\s+\w+\s*\(", re.MULTILINE)
            for i, line in enumerate(lines, 1):
                if func_pattern.search(line):
                    matches.append({"line": i, "text": line.strip()})

        elif search_type == "class":
            class_pattern = re.compile(r"^\s*class\s+\w+", re.MULTILINE)
            for i, line in enumerate(lines, 1):
                if class_pattern.search(line):
                    matches.append({"line": i, "text": line.strip()})

        elif search_type == "import":
            import_pattern = re.compile(r"^\s*(import|from)\s+\S+", re.MULTILINE)
            for i, line in enumerate(lines, 1):
                if import_pattern.search(line):
                    matches.append({"line": i, "text": line.strip()})

        elif search_type == "comment":
            comment_pattern = re.compile(r"^\s*#|^\s*\"\"\"|^\s*'''")
            for i, line in enumerate(lines, 1):
                if comment_pattern.search(line):
                    matches.append({"line": i, "text": line.strip()})

        else:  # regex
            try:
                compiled = re.compile(pattern)
                for i, line in enumerate(lines, 1):
                    if compiled.search(line):
                        matches.append({"line": i, "text": line.strip()})
            except re.error as e:
                return {"matches": [], "count": 0, "error": str(e)}

        return {
            "matches": matches,
            "count": len(matches),
        }
