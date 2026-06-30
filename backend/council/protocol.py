"""Protocol formatters for the Inverted Pyramid and Given-New communication pattern.

Every message between agents follows the Inverted Pyramid structure:
  HALLAZGO + ··· Detalle + ··· Impacto + ··· Propuesta
"""

from __future__ import annotations

import re
from typing import Any

from backend.models.schemas import Finding


# ──────────────────────────────────────────────
#  Formatting
# ──────────────────────────────────────────────


def format_finding(finding: Finding, include_agent: bool = False) -> str:
    """Convert a Finding to its Inverted Pyramid string representation.

    Parameters
    ----------
    finding : Finding
        The finding to format.
    include_agent : bool
        Prepend the agent name.

    Returns
    -------
    str
        Formatted finding string.
    """
    parts: list[str] = []
    if include_agent:
        parts.append(f"[{finding.agent}]")
    parts.append(f"HALLAZGO: {finding.hallazgo}")
    parts.append(f"··· Detalle: {finding.detalle}")
    parts.append(f"··· Impacto: {finding.impacto}")
    parts.append(f"··· Propuesta: {finding.propuesta}")
    return "\n".join(parts)


def format_findings_list(
    findings: list[Finding], include_agent: bool = False
) -> str:
    """Format multiple findings separated by blank lines."""
    return "\n\n".join(
        format_finding(f, include_agent=include_agent) for f in findings
    )


def format_round_header(round: int) -> str:
    """Return a header string for a given round."""
    titles = {
        1: "═══ RONDA 1: Análisis Individual ═══",
        2: "═══ RONDA 2: Debate Cruzado (Dado-Nuevo) ═══",
        3: "═══ RONDA 3: Refinamiento Final ═══",
    }
    return titles.get(round, f"═══ Ronda {round} ═══")


# ──────────────────────────────────────────────
#  Given-New prefix builder
# ──────────────────────────────────────────────


def add_dado_nuevo(
    previous_findings: list[Finding], my_finding: Finding
) -> str:
    """Build a Dado-Nuevo (Given-New) prefix for a finding.

    The prefix references a previous finding from another agent to create
    explicit cross-references (cohesion).

    Parameters
    ----------
    previous_findings : list[Finding]
        Findings from other agents in the previous round.
    my_finding : Finding
        The finding that the current agent is producing.

    Returns
    -------
    str
        A Dado-Nuevo prefixed version of the finding's hallazgo.
    """
    if not previous_findings:
        return my_finding.hallazgo

    # Try to find a related previous finding by keyword overlap
    my_keywords = _extract_keywords(my_finding.hallazgo)
    best_match: Finding | None = None
    best_score = 0

    for prev in previous_findings:
        if prev.agent == my_finding.agent:
            continue
        prev_keywords = _extract_keywords(prev.hallazgo)
        overlap = len(my_keywords & prev_keywords)
        if overlap > best_score:
            best_score = overlap
            best_match = prev

    if best_match is None:
        # Fallback: pick the first finding from a different agent
        for prev in previous_findings:
            if prev.agent != my_finding.agent:
                best_match = prev
                break

    if best_match is not None:
        prefix = (
            f"Coincidiendo con [{best_match.agent}] sobre "
            f"\"{best_match.hallazgo}\", agrego que: {my_finding.hallazgo}"
        )
        return prefix

    return my_finding.hallazgo


# ──────────────────────────────────────────────
#  Parsing
# ──────────────────────────────────────────────


def parse_finding(text: str) -> Finding | None:
    """Parse a single Inverted Pyramid text block into a Finding.

    Parameters
    ----------
    text : str
        Raw text from the LLM response.

    Returns
    -------
    Finding | None
    """
    lines = text.strip().split("\n")
    hallazgo = ""
    detalle = ""
    impacto = ""
    propuesta = ""

    # Try to extract agent name from prefix like "[security]"
    agent_match = re.match(r"^\[(\w+)\]", lines[0]) if lines else None
    agent = agent_match.group(1) if agent_match else "unknown"

    for line in lines:
        line = line.strip()
        if line.startswith("HALLAZGO:"):
            hallazgo = line[len("HALLAZGO:"):].strip()
        elif line.startswith("··· Detalle:") or line.startswith("···Detalle:"):
            detalle = line.split(":", 1)[1].strip() if ":" in line else ""
        elif line.startswith("··· Impacto:") or line.startswith("···Impacto:"):
            impacto = line.split(":", 1)[1].strip() if ":" in line else ""
        elif line.startswith("··· Propuesta:") or line.startswith("···Propuesta:"):
            propuesta = line.split(":", 1)[1].strip() if ":" in line else ""

    if not hallazgo:
        return None

    # Normalize impact
    impacto_lower = impacto.lower().strip()
    if "critico" in impacto_lower or "crítico" in impacto_lower:
        impacto = "Crítico"
    elif "alto" in impacto_lower:
        impacto = "Alto"
    elif "medio" in impacto_lower:
        impacto = "Medio"
    elif "bajo" in impacto_lower:
        impacto = "Bajo"
    else:
        impacto = "Medio"

    return Finding(
        agent=agent,
        hallazgo=hallazgo,
        detalle=detalle,
        impacto=impacto,
        propuesta=propuesta,
        ronda=0,
    )


# ──────────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────────


def _extract_keywords(text: str) -> set[str]:
    """Extract meaningful lowercase keywords from text."""
    stop_words = {
        "el", "la", "los", "las", "un", "una", "de", "del", "en", "por",
        "para", "con", "sin", "y", "e", "o", "a", "que", "es", "se",
        "su", "lo", "como", "más", "pero", "sus", "le", "ya", "este",
        "entre", "porque", "era", "muy", "sin", "sobre", "también",
        "tras", "había", "coincidiendo", "discrepo", "complementando",
        "agrego", "dice", "sobre", "que",
    }
    words = re.findall(r"\w{4,}", text.lower())
    return {w for w in words if w not in stop_words}
