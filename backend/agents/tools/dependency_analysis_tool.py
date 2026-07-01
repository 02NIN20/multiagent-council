"""Tool to analyse code dependencies and imports."""

from __future__ import annotations

import re
from typing import Any

from backend.agents.tools.base_tool import BaseTool


class DependencyAnalysisTool(BaseTool):
    """Analyse imports, dependencies, and coupling between modules."""

    def __init__(self) -> None:
        super().__init__(
            name="dependency_analysis",
            description="Analyse imports, external dependencies, and module coupling.",
        )

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        """Analyse dependencies in source code.

        Parameters
        ----------
        code : str
            Source code to analyse.

        Returns
        -------
        dict with keys: imports (list), external_deps (list), circular_deps (list)
        """
        code: str = kwargs.get("code", "")
        if not code:
            return {"imports": [], "external_deps": [], "circular_deps": []}

        imports = []
        for line in code.split("\n"):
            stripped = line.strip()
            if stripped.startswith("import ") or stripped.startswith("from "):
                imports.append(stripped)

        # Categorise imports
        std_libs = {"os", "sys", "json", "re", "math", "datetime", "time",
                    "collections", "functools", "itertools", "typing",
                    "hashlib", "sqlite3", "http", "io", "csv", "abc",
                    "pathlib", "uuid", "logging", "asyncio"}

        external_deps = []
        for imp in imports:
            parts = imp.split()
            if imp.startswith("import "):
                module = parts[1].split(".")[0]
            else:  # from X import Y
                module = parts[1].split(".")[0]
            if module not in std_libs:
                external_deps.append(module)

        return {
            "imports": imports,
            "external_deps": list(set(external_deps)),
            "import_count": len(imports),
            "external_dep_count": len(set(external_deps)),
        }
