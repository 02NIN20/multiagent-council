"""Synthesis engine — consolidates findings across agents and rounds.

Produces the final Report with consensus levels and vote counts.
"""

from __future__ import annotations

import logging
from collections import Counter
from difflib import SequenceMatcher
from typing import Any

from backend.models.schemas import ConsolidatedFinding, Finding, Report

logger = logging.getLogger(__name__)

# Minimum similarity ratio to consider two findings as the same topic
SIMILARITY_THRESHOLD = 0.35


def synthesize(all_findings: dict[int, list[Finding]]) -> Report:
    """Synthesize findings from all rounds into a final Report.

    Parameters
    ----------
    all_findings : dict[int, list[Finding]]
        Mapping of round number → list of Finding from all agents.

    Returns
    -------
    Report
        Consolidated report with consensus analysis.
    """
    logger.info(
        "Synthesizing %d rounds of findings",
        len(all_findings),
    )

    # Collect final-round findings (round 3) as the primary source
    # Fall back to round 2, then round 1
    final_findings: list[Finding] = []
    for r in (3, 2, 1):
        if r in all_findings and all_findings[r]:
            final_findings = all_findings[r]
            break

    if not final_findings:
        logger.warning("No findings to synthesize")
        return Report(
            findings=[],
            summary="No se encontraron hallazgos en ninguna ronda.",
            rounds=len(all_findings),
        )

    # Cluster similar findings
    clusters = _cluster_findings(final_findings)

    # Build consolidated findings
    consolidated: list[ConsolidatedFinding] = []
    for cluster in clusters:
        cf = _consolidate_cluster(cluster)
        if cf is not None:
            consolidated.append(cf)

    # Sort by severity: Crítico → Alto → Medio → Bajo
    severity_order = {"Crítico": 0, "Alto": 1, "Medio": 2, "Bajo": 3}
    consolidated.sort(
        key=lambda x: severity_order.get(x.impacto, 99)
    )

    # Build executive summary
    summary = _build_summary(consolidated)

    return Report(
        findings=consolidated,
        summary=summary,
        rounds=len(all_findings),
    )


# ──────────────────────────────────────────────
#  Internal helpers
# ──────────────────────────────────────────────


def _cluster_findings(findings: list[Finding]) -> list[list[Finding]]:
    """Group similar findings into clusters based on text similarity."""
    clusters: list[list[Finding]] = []

    for finding in findings:
        best_cluster_idx = -1
        best_score = 0.0

        for idx, cluster in enumerate(clusters):
            representative = cluster[0]
            score = _text_similarity(
                finding.hallazgo, representative.hallazgo
            )
            if score > best_score and score >= SIMILARITY_THRESHOLD:
                best_score = score
                best_cluster_idx = idx

        if best_cluster_idx >= 0:
            clusters[best_cluster_idx].append(finding)
        else:
            clusters.append([finding])

    return clusters


def _consolidate_cluster(
    cluster: list[Finding],
) -> ConsolidatedFinding | None:
    """Merge a cluster of similar findings into one ConsolidatedFinding."""
    if not cluster:
        return None

    # Pick the representative: longest hallazgo from the highest-impact agent
    severity_order = {"Crítico": 0, "Alto": 1, "Medio": 2, "Bajo": 3}
    cluster_sorted = sorted(
        cluster,
        key=lambda f: (
            severity_order.get(f.impacto, 99),
            -len(f.hallazgo),
        ),
    )
    rep = cluster_sorted[0]

    # Gather votes: agent → impacto
    votes: dict[str, str] = {}
    for f in cluster:
        votes[f.agent] = f.impacto

    # Calculate consensus
    total_agents = 5
    voting_agents = len(votes)
    consensus_score = voting_agents / total_agents

    if consensus_score >= 0.8:
        consensus_level = "Alto"
    elif consensus_score >= 0.5:
        consensus_level = "Medio"
    elif consensus_score >= 0.2:
        consensus_level = "Bajo"
    else:
        consensus_level = "Sin consenso"

    # Merge details
    all_details = list({f.detalle for f in cluster if f.detalle})
    merged_detail = " | ".join(all_details) if all_details else rep.detalle

    # Pick the strongest propuesta (from highest-impact finding)
    propuesta = rep.propuesta

    return ConsolidatedFinding(
        hallazgo=rep.hallazgo,
        detalle=merged_detail,
        impacto=rep.impacto,
        propuesta=propuesta,
        votes=votes,
        consensus_level=consensus_level,
        consensus_score=round(consensus_score, 2),
    )


def _build_summary(consolidated: list[ConsolidatedFinding]) -> str:
    """Generate an executive summary from consolidated findings."""
    if not consolidated:
        return "No se encontraron hallazgos."

    criticos = sum(1 for f in consolidated if f.impacto == "Crítico")
    altos = sum(1 for f in consolidated if f.impacto == "Alto")
    medios = sum(1 for f in consolidated if f.impacto == "Medio")
    bajos = sum(1 for f in consolidated if f.impacto == "Bajo")
    alto_consenso = sum(
        1 for f in consolidated if f.consensus_level == "Alto"
    )

    parts: list[str] = [
        f"Se encontraron {len(consolidated)} hallazgos: "
        f"{criticos} críticos, {altos} altos, {medios} medios, {bajos} bajos. "
        f"{alto_consenso} hallazgos tienen alto consenso entre los agentes."
    ]

    if criticos > 0:
        parts.append(
            f"⚠️ Se recomienda atención inmediata a los {criticos} hallazgos críticos."
        )

    return " ".join(parts)


def _text_similarity(a: str, b: str) -> float:
    """Compute string similarity ratio (0.0 – 1.0)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()
