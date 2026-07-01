"""CodeWriter sub-agent — generates and writes fixes to code."""

from __future__ import annotations

from typing import Any

from backend.agents.subagents.base_subagent import BaseSubAgent


class CodeWriter(BaseSubAgent):
    """Generates fixes and implementations for code."""

    def __init__(self) -> None:
        super().__init__(
            name="code_writer",
            specialty="generating fixes and code implementations",
        )

    async def write_fix(self, code: str, finding: dict[str, Any]) -> str:
        """Generates fixed code for a given finding.

        Parameters
        ----------
        code : str
            Original source code.
        finding : dict
            Finding with issue details (title, location, severity, etc.).

        Returns
        -------
        str
            Fixed code with the issue resolved.
        """
        if not code.strip():
            return ""

        # Extract finding details
        title = finding.get("title", "") or finding.get("pattern", "")
        location = finding.get("location", "")
        severity = finding.get("severity", "")
        description = finding.get("description", "")
        fix_proposal = finding.get("fix", "") or finding.get("proposal", "")

        prompt = (
            f"Fix the following code based on the finding.\n\n"
            f"Original Code:\n```\n{code[:2000]}\n```\n\n"
            f"Finding:\n"
            f"Title: {title}\n"
            f"Location: {location}\n"
            f"Severity: {severity}\n"
            f"Description: {description}\n"
            f"Fix Proposal: {fix_proposal}\n\n"
            f"Requirements:\n"
            f"1. Generate ONLY the fixed code (no comments about changes)\n"
            f"2. If finding is not applicable, return the original code\n"
            f"3. Preserve code style and formatting\n"
            f"4. Ensure the fix actually resolves the finding\n"
            f"5. Return only code within triple backticks (```)\n"
        )

        response = await self._call_llm(
            system_prompt="You are a skilled code fix generator. Generate precise, efficient fixes that actually resolve issues.",
            user_prompt=prompt,
            max_tokens=2048,
            temperature=0.1,
        )

        # Extract code from backticks
        if "```" in response:
            code_blocks = response.split("```")
            if len(code_blocks) >= 2:
                return code_blocks[1].strip()

        return response.strip()

    async def generate_implementation(self, spec: str) -> str:
        """Generates code implementation from specification.

        Parameters
        ----------
        spec : str
            Specification or requirements for the code to generate.

        Returns
        -------
        str
            Generated code implementation.
        """
        if not spec.strip():
            return ""

        prompt = (
            f"Generate complete implementation based on this specification:\n\n"
            f"Specification:\n{spec}\n\n"
            f"Requirements:\n"
            f"1. Generate complete, production-ready code\n"
            f"2. Include necessary imports and dependencies\n"
            f"3. Add appropriate error handling and validation\n"
            f"4. Follow Python best practices\n"
            f"5. Use type hints and docstrings\n"
            f"6. Return only the code within triple backticks (```)\n"
            f"7. No extra explanations or comments about the code\n"
        )

        response = await self._call_llm(
            system_prompt="You are an expert Python developer. Generate clean, efficient, production-ready code from specifications.",
            user_prompt=prompt,
            max_tokens=4096,
            temperature=0.2,
        )

        # Extract code from backticks
        if "```" in response:
            code_blocks = response.split("```")
            if len(code_blocks) >= 2:
                return code_blocks[1].strip()

        return response.strip()
