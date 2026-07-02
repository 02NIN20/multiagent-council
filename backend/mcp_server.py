"""MCP server for Multi-Agent Council.

Exposes the Agent Society directly (no HTTP API needed) as MCP tools
for OpenCode, Claude Desktop, Cursor, and any MCP-compatible client.

Usage:
    python3 -m backend.mcp_server
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)
server = FastMCP("multiagent-council")

# Lazy import — the orchestrator is heavy and imports many things,
# so we only load it when a tool is actually called.
_orchestrator: Any = None


def _get_orchestrator():
    """Import and cache the CouncilOrchestrator singleton."""
    global _orchestrator
    if _orchestrator is None:
        from backend.council.orchestrator import CouncilOrchestrator
        _orchestrator = CouncilOrchestrator()
    return _orchestrator


def _call_llm(system: str, prompt: str, max_tokens: int = 2048) -> str:
    """Direct LLM call for tools that don't need the full council."""
    import asyncio
    from openai import AsyncOpenAI
    from backend.config import settings
    client = AsyncOpenAI(
        api_key=settings.llm_api_key,
        base_url=settings.llm_base_url,
        timeout=settings.llm_timeout_seconds,
    )
    response = asyncio.run(
        client.chat.completions.create(
            model=settings.llm_model,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=max_tokens,
        )
    )
    return response.choices[0].message.content or ""


async def _run_review(code: str, instruction: str = "", mode: str = "light") -> str:
    """Run a council review and return formatted JSON."""
    orch = _get_orchestrator()
    report, session_id, round_data = await orch.run_council(
        code=code,
        instruction=instruction or None,
        mode=mode,
    )
    findings = report.findings or []
    return json.dumps({
        "session_id": session_id,
        "findings_count": len(findings),
        "summary": report.summary,
        "risk_overview": report.risk_overview,
        "remediation_roadmap": report.remediation_roadmap,
        "token_usage": report.token_usage,
        "findings": [
            {"title": f.title, "impact": f.impact,
             "detail": f.detail[:200], "proposal": f.proposal[:200]}
            for f in findings[:20]
        ],
    }, indent=2)


# ── Tools ──────────────────────────────────────────────────────────


@server.tool()
async def review_code(code: str, instruction: str = "", mode: str = "light") -> str:
    """Run a full multi-agent code review with 6 specialized agents.

    The code is analyzed through 3 debate rounds (individual → cross-debate
    → refinement). Each agent delegates to 2-3 sub-agents (SecurityAuditor,
    CodeWriter, StaticAnalyzer, etc.).

    light mode: 3 agents, 2 rounds, budget $0.20 (∼60s)
    full mode: 6 agents, 3 rounds, budget $1.00 (∼180s)

    Args:
        code: The complete source code to review.
        instruction: Optional focus area (e.g. "Focus on SQL injection").
        mode: "light" for speed (default), "full" for thoroughness.
    """
    try:
        return await _run_review(code, instruction, mode)
    except Exception as e:
        logger.exception("review_code failed")
        return json.dumps({"error": str(e)[:300], "tool": "review_code"})


@server.tool()
async def chat(message: str) -> str:
    """Ask a question to the Agent Society (6 AI agents).

    The question is routed to 1-3 relevant agents depending on topic.
    Each agent answers from its role perspective, then answers are merged.

    Args:
        message: Your question for the agents.
    """
    try:
        from backend.main import _classify_question, _route_question, _synthesize_chat
        from backend.agents.core.coordinator_agent import CoordinatorAgent
        from backend.agents.core.analyst_agent import AnalystAgent
        from backend.agents.core.architect_agent import ArchitectAgent
        from backend.agents.core.engineer_agent import EngineerAgent
        from backend.agents.core.critic_agent import CriticAgent
        from backend.agents.core.researcher_agent import ResearcherAgent

        agents = {
            "coordinator": CoordinatorAgent(),
            "analyst": AnalystAgent(),
            "architect": ArchitectAgent(),
            "engineer": EngineerAgent(),
            "critic": CriticAgent(),
            "researcher": ResearcherAgent(),
        }

        category = _classify_question(message)
        selected = _route_question(category, has_images=False)

        import asyncio
        async def ask(name, agent):
            try:
                ans = await agent.answer_question(message)
                return {"agent": name, "role": agent.role_description, "answer": ans}
            except Exception as e:
                return {"agent": name, "role": "", "answer": f"[unavailable: {e}]"}

        tasks = [ask(name, agent) for name, agent in selected if name in agents]
        contributions = await asyncio.gather(*tasks)
        final = await _synthesize_chat(message, contributions)

        return json.dumps({
            "response": final,
            "agents": [{"name": c["agent"], "role": c["role"], "answer": c["answer"][:300]}
                       for c in contributions],
        }, indent=2)
    except Exception as e:
        logger.exception("chat failed")
        return json.dumps({"error": str(e)[:300], "tool": "chat"})


@server.tool()
async def analyze_file(filename: str, content: str, question: str = "") -> str:
    """Analyze a file using the appropriate agent.

    For code: runs a full council review.
    For text/math/research: uses Analyst + Researcher agents.

    Args:
        filename: File name (e.g. "main.py").
        content: Full file content.
        question: Optional specific question.
    """
    try:
        from backend.utils.content_detector import detect_content_type
        ct = detect_content_type(filename, content)

        if ct == "code":
            return await _run_review(content, question or f"Analyze {filename}", mode="light")

        # Non-code: direct LLM with role-appropriate prompt
        prompts = {
            "math": "You are a math expert. Explain equations clearly using LaTeX.",
            "research": "You are a research analyst. Summarize findings objectively.",
            "markdown": "You are a document editor. Provide feedback on structure.",
        }
        system = prompts.get(ct, "You are a content analyst. Answer the question.")
        truncated = content[:4000]
        prompt = f"Analyze {filename} ({ct}):\n{question or 'What does this do?'}\n\n```\n{truncated}\n```"
        result = _call_llm(system, prompt)
        return json.dumps({"filename": filename, "type": ct, "analysis": result}, indent=2)
    except Exception as e:
        logger.exception("analyze_file failed")
        return json.dumps({"error": str(e)[:300], "tool": "analyze_file"})


@server.tool()
async def generate_code(specification: str, language: str = "python") -> str:
    """Generate code from a specification.

    Args:
        specification: What to build (e.g. "FastAPI CRUD for users with SQLite").
        language: Target language (python, javascript, go, rust, etc.).
    """
    try:
        prompt = (
            f"Generate complete {language} code:\n{specification}\n\n"
            f"Requirements:\n- Production-ready\n- Error handling\n"
            f"- Best practices for {language}"
        )
        result = _call_llm(f"You are an expert {language} developer.", prompt, max_tokens=4096)
        return json.dumps({"language": language, "code": result}, indent=2)
    except Exception as e:
        logger.exception("generate_code failed")
        return json.dumps({"error": str(e)[:300], "tool": "generate_code"})


@server.tool()
async def implement_fix(code: str, issue: str) -> str:
    """Fix a bug or code issue.

    Args:
        code: The current code with the issue.
        issue: Description of what's wrong (e.g. "SQL injection in line 12").
    """
    try:
        prompt = f"Fix this:\nIssue: {issue}\n\nCode:\n```\n{code}\n```\n\nOutput corrected code + explanation."
        result = _call_llm("You are an expert developer. Fix the issue.", prompt, max_tokens=4096)
        return json.dumps({"issue": issue, "fix": result}, indent=2)
    except Exception as e:
        logger.exception("implement_fix failed")
        return json.dumps({"error": str(e)[:300], "tool": "implement_fix"})


# ── Main ───────────────────────────────────────────────────────────


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    logger.info("Multi-Agent Council MCP server starting (stdio)")
    logger.info("Model: qwen3-coder-plus-2025-09-23 (set via .env or env vars)")
    logger.info("Tools: review_code, chat, analyze_file, generate_code, implement_fix")
    try:
        server.run(transport="stdio")
    except KeyboardInterrupt:
        logger.info("Server stopped")


if __name__ == "__main__":
    main()
