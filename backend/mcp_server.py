"""MCP (Model Context Protocol) server for Qwen Council.

Exposes the Agent Society as tools for OpenCode, Claude Desktop, Cursor, etc.

Tools:
  - review_code: Submit code for multi-agent council review
  - analyze_file: Submit a file for Agent Society analysis
  - chat: Ask the Agent Society a question
  - list_sessions: List past sessions
  - get_session: Get session details

Usage:
    QWEN_COUNCIL_API_URL=http://47.84.227.185 python3 -m backend.mcp_server
"""

from __future__ import annotations

import json
import logging
import os

import httpx
from mcp.server.fastmcp import FastMCP

logger = logging.getLogger(__name__)

API_BASE_URL = os.environ.get("QWEN_COUNCIL_API_URL", "http://localhost:8000")
server = FastMCP("qwen-council")


async def api_post(path: str, data: dict) -> dict:
    url = f"{API_BASE_URL.rstrip('/')}{path}"
    async with httpx.AsyncClient(timeout=600) as client:
        resp = await client.post(url, json=data, headers={"Content-Type": "application/json"})
        resp.raise_for_status()
        return resp.json()


async def api_get(path: str) -> dict:
    url = f"{API_BASE_URL.rstrip('/')}{path}"
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.json()


@server.tool()
async def review_code(code: str, instruction: str = "", mode: str = "light") -> str:
    """Submit source code for multi-agent council review.

    6 core agents (Coordinator, Analyst, Architect, Engineer, Critic, Researcher)
    with 15 sub-agents analyze code through debate rounds + negotiation.

    Use mode="light" for faster results (3 agents, 2 rounds, ~40% cost).
    Use mode="full" for thorough review (6 agents, 4 rounds, takes longer).

    Args:
        code: Source code to review.
        instruction: Optional focus instruction (e.g. "Focus on security").
        mode: Review mode - "light" (fast) or "full" (thorough). Default: "light".
    """
    payload = {"code": code, "mode": mode}
    if instruction:
        payload["instruction"] = instruction

    result = await api_post("/api/review", payload)
    report = result.get("report", {})

    return json.dumps({
        "session_id": result.get("session_id"),
        "findings_count": len(report.get("findings", [])),
        "summary": report.get("summary", ""),
        "token_usage": report.get("token_usage", {}),
        "findings": [
            {"title": f.get("title"), "impact": f.get("impact"),
             "proposal": f.get("proposal"), "consensus": f.get("consensus_level")}
            for f in report.get("findings", [])[:15]
        ],
    }, indent=2)


@server.tool()
async def generate_code(specification: str, language: str = "python") -> str:
    """Generate code from a specification using the Engineer agent.

    The Engineer agent writes implementation code based on your requirements.

    Args:
        specification: What code to generate (e.g. "A Flask REST API with SQLite").
        language: Programming language (python, javascript, typescript, etc.).

    Returns:
        Generated code with explanation.
    """
    from openai import AsyncOpenAI
    from backend.config import settings

    client = AsyncOpenAI(api_key=settings.qwen_api_key, base_url=settings.qwen_base_url)
    prompt = (
        f"Generate {language} code for the following specification.\n\n"
        f"Specification: {specification}\n\n"
        f"Output the complete code implementation with:\n"
        f"- Well-structured {language} code\n"
        f"- Comments explaining key sections\n"
        f"- Error handling where appropriate\n"
        f"- Best practices for {language}\n"
    )
    response = await client.chat.completions.create(
        model=settings.qwen_model,
        messages=[
            {"role": "system", "content": f"You are an expert {language} developer. Write clean, production-ready code."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=4096,
    )
    result = response.choices[0].message.content or ""
    return json.dumps({
        "language": language,
        "specification": specification,
        "generated_code": result,
    }, indent=2)


@server.tool()
async def implement_fix(code: str, issue: str) -> str:
    """Generate a code fix for a specific issue using the Engineer agent.

    The Engineer agent analyzes the problem and produces corrected code.

    Args:
        code: The current code with the issue.
        issue: Description of what's wrong or what to fix.

    Returns:
        Fixed code with explanation of changes.
    """
    from openai import AsyncOpenAI
    from backend.config import settings

    client = AsyncOpenAI(api_key=settings.qwen_api_key, base_url=settings.qwen_base_url)
    prompt = (
        f"Fix the following issue in this code.\n\n"
        f"Issue: {issue}\n\n"
        f"Code:\n```\n{code}\n```\n\n"
        f"Output:\n"
        f"- The corrected/fixed code\n"
        f"- Brief explanation of what was wrong and what changed\n"
        f"- Testing suggestions if applicable"
    )
    response = await client.chat.completions.create(
        model=settings.qwen_model,
        messages=[
            {"role": "system", "content": "You are an expert developer. Fix code issues and explain your changes."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
        max_tokens=4096,
    )
    result = response.choices[0].message.content or ""
    return json.dumps({
        "original_issue": issue,
        "fixed_code": result,
    }, indent=2)
    """Submit a file for the Agent Society to analyze.

    All 6 agents examine the file and provide domain-specific insights.

    Args:
        filename: File name (e.g. "main.py").
        content: File contents as text.
        question: Optional specific question about the file.
    """
    payload = {
        "message": question or f"Analyze this file: {filename}",
        "files": [{"filename": filename, "content": content, "language": filename.split('.')[-1]}],
    }
    result = await api_post("/api/chat", payload)

    return json.dumps({
        "session_id": result.get("session_id"),
        "response": result.get("response", ""),
        "agents": [
            {"agent": c.get("agent"), "role": c.get("role_description"), "answer": c.get("answer")}
            for c in result.get("agent_contributions", [])
        ],
    }, indent=2)


@server.tool()
async def analyze_file(filename: str, content: str, question: str = "") -> str:
    """Submit a file for the Agent Society to analyze.

    All agents examine the file from their domain perspective.
    For large files, analysis is focused on the first part of the file.

    Args:
        filename: File name (e.g. "main.py").
        content: File contents as text (max 50000 chars).
        question: Optional specific question about the file.
    """
    if len(content) > 50000:
        return json.dumps({
            "error": "File too large (max 50000 chars)", "filename": filename,
        }, indent=2)

    # Use direct LLM for files > 3000 chars (faster)
    if len(content) > 3000:
        from openai import AsyncOpenAI
        from backend.config import settings
        client = AsyncOpenAI(api_key=settings.qwen_api_key, base_url=settings.qwen_base_url)
        truncated = content[:4000]
        prompt = (
            f"Analyze this {filename} file.\nQuestion: {question or 'What does this do?'}\n\n"
            f"```\n{truncated}\n```\n(truncated)\n\n"
            f"Provide: overview, key components, potential issues."
        )
        resp = await client.chat.completions.create(
            model=settings.qwen_model,
            messages=[
                {"role": "system", "content": "You are a code analyst. Provide concise, insightful analysis."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2, max_tokens=2048,
        )
        result = resp.choices[0].message.content or ""
        return json.dumps({"filename": filename, "analysis": result,
                          "truncated": len(content) > 4000}, indent=2)

    # Small files → route through chat agents
    payload = {
        "message": question or f"Analyze this file: {filename}",
        "files": [{"filename": filename, "content": content,
                   "language": filename.split('.')[-1]}],
    }
    result = await api_post("/api/chat", payload)
    return json.dumps({
        "session_id": result.get("session_id"),
        "response": result.get("response", ""),
        "agents": [
            {"agent": c.get("agent"), "role": c.get("role_description"),
             "answer": c.get("answer")}
            for c in result.get("agent_contributions", [])
        ],
    }, indent=2)


@server.tool()
async def chat(message: str, session_id: str = "") -> str:
    """Ask the Agent Society a question.

    6 core agents answer. A router activates only the 1-3 most relevant.

    Args:
        message: Your question.
        session_id: Optional session ID for conversation context.
    """
    payload = {"message": message}
    if session_id:
        payload["session_id"] = session_id

    result = await api_post("/api/chat", payload)
    return json.dumps({
        "session_id": result.get("session_id"),
        "response": result.get("response", ""),
        "agents": [
            {"name": c.get("agent"), "role": c.get("role_description"), "answer": c.get("answer")}
            for c in result.get("agent_contributions", [])
        ],
    }, indent=2)


@server.tool()
async def list_sessions(limit: int = 20) -> str:
    """List past review and chat sessions.

    Args:
        limit: Max sessions to return (default 20).
    """
    sessions = await api_get("/api/sessions")
    return json.dumps(sessions[:limit], indent=2)


@server.tool()
async def get_session(session_id: str) -> str:
    """Get details of a specific session.

    Args:
        session_id: Session ID to retrieve.
    """
    session = await api_get(f"/api/sessions/{session_id}")
    return json.dumps(session, indent=2)


def main():
    logging.basicConfig(level=logging.INFO)
    logger.info("Starting Qwen Council MCP server (stdio)")
    logger.info("API URL: %s", API_BASE_URL)
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
