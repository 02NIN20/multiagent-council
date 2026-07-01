"""SecurityAuditor sub-agent — performs security audits on code."""

from __future__ import annotations

from typing import Any

from backend.agents.subagents.base_subagent import BaseSubAgent


class SecurityAuditor(BaseSubAgent):
    """Performs security audits and identifies vulnerabilities."""

    def __init__(self) -> None:
        super().__init__(
            name="security_auditor",
            specialty="performing security audits and identifying vulnerabilities",
        )

    async def audit_security(self, code: str) -> list[dict[str, Any]]:
        """Performs security audit.

        Parameters
        ----------
        code : str
            Source code to audit.

        Returns
        -------
        list of finding dicts with keys: title, severity, cwe, location, fix.
        """
        if not code.strip():
            return []

        prompt = (
            f"Perform a comprehensive security audit of this code.\n\n"
            f"Code:\n```\n{code[:3000]}\n```\n\n"
            f"Identify security issues including:\n"
            f"1. OWASP Top 10 vulnerabilities\n"
            f"2. Common security anti-patterns\n"
            f"3. CWE references (Common Weakness Enumeration)\n"
            f"4. Authentication/authorization issues\n"
            f"5. Input validation problems\n"
            f"6. SQL injection risks\n"
            f"7. XSS vulnerabilities\n"
            f"8. Insecure cryptography\n"
            f"9. Session management issues\n"
            f"10. Error handling that leaks information\n\n"
            f"For each issue, return:\n"
            f"TITLE: <issue title>\n"
            f"SEVERITY: <Critical|High|Medium|Low>\n"
            f"CWE: <CWE identifier if applicable, otherwise 'N/A'>\n"
            f"LOCATION: <line numbers or code section>\n"
            f"FIX: <step-by-step fix to resolve>\n\n"
            f"If no issues found, return: NO_VULNERABILITIES\n"
            f"Separate each finding with '---' separator."
        )

        response = await self._call_llm(
            system_prompt="You are a security expert. Perform comprehensive security audits and identify OWASP Top 10 vulnerabilities.",
            user_prompt=prompt,
            max_tokens=2048,
            temperature=0.1,
        )

        if response.strip() == "NO_VULNERABILITIES":
            return []

        findings = []
        blocks = response.strip().split("---")
        for block in blocks:
            if not block.strip():
                continue
            finding = {}
            lines = block.strip().split("\n")
            for line in lines:
                line = line.strip()
                if line.startswith("TITLE:"):
                    finding["title"] = line[6:].strip()
                elif line.startswith("SEVERITY:"):
                    finding["severity"] = line[9:].strip()
                elif line.startswith("CWE:"):
                    finding["cwe"] = line[4:].strip()
                elif line.startswith("LOCATION:"):
                    finding["location"] = line[9:].strip()
                elif line.startswith("FIX:"):
                    finding["fix"] = line[5:].strip()
            if finding.get("title"):
                findings.append(finding)
        return findings
