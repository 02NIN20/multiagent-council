"""Tests for core agents — Inverted Pyramid format, NO_FINDINGS, Given-New."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest

# Some tests create agents directly (no fixture). Prevent OpenAI SDK v2 from
# raising at client instantiation by patching before the agent classes are loaded.
os.environ.setdefault("OPENAI_API_KEY", "sk-test-fake-key-for-tests")
_patcher = patch("backend.agents.base_agent.AsyncOpenAI", autospec=True)
_mock_client_cls = _patcher.start()
_mock_client_cls.return_value = MagicMock()

from backend.agents.core.coordinator_agent import CoordinatorAgent
from backend.agents.core.analyst_agent import AnalystAgent
from backend.agents.core.architect_agent import ArchitectAgent
from backend.agents.core.engineer_agent import EngineerAgent
from backend.agents.core.critic_agent import CriticAgent
from backend.agents.core.researcher_agent import ResearcherAgent
from backend.models.schemas import Finding
from backend.tests.conftest import SAMPLE_CODE_VULNERABLE, SAMPLE_CODE_CLEAN


# ──────────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────────

ALL_AGENT_CLASSES = [
    CoordinatorAgent,
    AnalystAgent,
    ArchitectAgent,
    EngineerAgent,
    CriticAgent,
    ResearcherAgent,
]


def assert_inverted_pyramid(finding: Finding) -> None:
    """Verify a Finding has all Inverted Pyramid fields populated."""
    assert finding.title, "FINDING (title) must not be empty"
    assert finding.detail, "Detail must not be empty"
    assert finding.impact in (
        "Critical",
        "High",
        "Medium",
        "Low",
    ), f"Impact must be one of Critical|High|Medium|Low, got {finding.impact}"
    assert finding.proposal, "Proposal must not be empty"
    assert finding.agent, "Agent name must not be empty"
    assert finding.round_num in (1, 2, 3), f"Round must be 1, 2, or 3, got {finding.round_num}"


# ──────────────────────────────────────────────
#  Tests – Inverted Pyramid format
# ──────────────────────────────────────────────


@pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES)
@pytest.mark.asyncio
async def test_agent_returns_inverted_pyramid_findings(agent_cls, mock_qwen_client):
    """Each agent produces Findings with all Inverted Pyramid fields."""
    agent = agent_cls()
    findings = await agent.analyze(code=SAMPLE_CODE_VULNERABLE, round=1)
    assert len(findings) > 0, f"{agent.name} should have found issues"
    for f in findings:
        assert_inverted_pyramid(f)


@pytest.mark.asyncio
async def test_critic_agent_name(mock_qwen_client):
    """The critic agent name matches the finding agent field."""
    agent = CriticAgent()
    findings = await agent.analyze(code=SAMPLE_CODE_VULNERABLE, round=1)
    for f in findings:
        assert f.agent == "critic"


@pytest.mark.asyncio
async def test_analyst_agent_name(mock_qwen_client):
    agent = AnalystAgent()
    findings = await agent.analyze(code=SAMPLE_CODE_VULNERABLE, round=1)
    for f in findings:
        assert f.agent == "analyst"


@pytest.mark.asyncio
async def test_architect_agent_name(mock_qwen_client):
    agent = ArchitectAgent()
    findings = await agent.analyze(code=SAMPLE_CODE_VULNERABLE, round=1)
    for f in findings:
        assert f.agent == "architect"


@pytest.mark.asyncio
async def test_engineer_agent_name(mock_qwen_client):
    agent = EngineerAgent()
    findings = await agent.analyze(code=SAMPLE_CODE_VULNERABLE, round=1)
    for f in findings:
        assert f.agent == "engineer"


@pytest.mark.asyncio
async def test_researcher_agent_name(mock_qwen_client):
    agent = ResearcherAgent()
    findings = await agent.analyze(code=SAMPLE_CODE_VULNERABLE, round=1)
    for f in findings:
        assert f.agent == "researcher"


# ──────────────────────────────────────────────
#  Tests – NO_FINDINGS
# ──────────────────────────────────────────────


@pytest.mark.parametrize("agent_cls", ALL_AGENT_CLASSES)
@pytest.mark.asyncio
async def test_empty_code_returns_no_findings(agent_cls, mock_qwen_client_no_findings):
    """When the LLM returns 'NO_FINDINGS', the agent returns an empty list."""
    agent = agent_cls()
    findings = await agent.analyze(code="", round=1)
    assert findings == [], f"{agent.name} should return [] for empty code"


@pytest.mark.asyncio
async def test_critic_agent_no_findings_on_clean_code(mock_qwen_client_no_findings):
    """Clean code produces no findings."""
    agent = CriticAgent()
    findings = await agent.analyze(code=SAMPLE_CODE_CLEAN, round=1)
    assert findings == []


# ──────────────────────────────────────────────
#  Tests – Given-New in Round 2
# ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_agent_receives_context_in_round_2(mock_qwen_client_given_new):
    """In Round 2, the agent receives other agents' findings as context."""
    agent = CriticAgent()
    context = [
        {
            "agent": "architect",
            "title": "No separation of concerns",
            "detail": "Mixing DB and business logic",
            "impact": "High",
            "proposal": "Extract repository pattern",
        }
    ]
    findings = await agent.analyze(
        code=SAMPLE_CODE_VULNERABLE, context=context, round=2
    )
    assert len(findings) > 0
    assert any("Agreeing" in f.title or "validation" in f.title for f in findings)


@pytest.mark.asyncio
async def test_round_2_context_passed_to_llm(mock_qwen_client):
    """Verify the context block is included in the user prompt for round 2."""
    agent = CriticAgent()
    context = [
        {
            "agent": "architect",
            "title": "No separation of concerns",
            "detail": "Mixing DB and business logic",
            "impact": "High",
            "proposal": "Extract repository pattern",
        }
    ]
    prompt = agent._build_user_prompt(code=SAMPLE_CODE_VULNERABLE, context=context, round=2)
    assert "Previous round findings" in prompt
    assert "architect" in prompt
    assert "No separation of concerns" in prompt
    assert "Round 2: Cross-Debate" in prompt or "Round 2" in prompt
    assert "Given-New" in prompt or "given" in prompt.lower()


# ──────────────────────────────────────────────
#  Tests – Round-specific prompts
# ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_round_1_prompt_has_no_context(mock_qwen_client):
    """Round 1 prompt should not contain previous round context."""
    agent = CriticAgent()
    prompt = agent._build_user_prompt(code=SAMPLE_CODE_VULNERABLE, round=1)
    assert "Previous round findings" not in prompt
    assert "Round 1: Individual Analysis" in prompt or "Round 1" in prompt


@pytest.mark.asyncio
async def test_round_3_prompt_has_keep_modify_withdraw(mock_qwen_client):
    """Round 3 prompt should instruct the agent about KEEP/MODIFY/WITHDRAW."""
    agent = CriticAgent()
    prompt = agent._build_user_prompt(code=SAMPLE_CODE_VULNERABLE, round=3)
    assert "Round 3: Final Refinement" in prompt or "Round 3" in prompt
    assert "KEEP" in prompt
    assert "MODIFY" in prompt
    assert "WITHDRAW" in prompt


# ──────────────────────────────────────────────
#  Tests – Response parsing
# ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_parse_no_findings():
    """NO_FINDINGS text is parsed to an empty list."""
    agent = CriticAgent()
    findings = agent._parse_findings("NO_FINDINGS", round=1)
    assert findings == []


@pytest.mark.asyncio
async def test_parse_empty_text():
    """Empty text is parsed to an empty list."""
    agent = CriticAgent()
    findings = agent._parse_findings("", round=1)
    assert findings == []


@pytest.mark.asyncio
async def test_parse_single_finding():
    """A single Inverted Pyramid block is correctly parsed."""
    agent = CriticAgent()
    text = (
        "FINDING: SQL injection in query\n"
        "··· Detail: Unsanitized input at line 5\n"
        "··· Impact: Critical\n"
        "··· Proposal: Use parameterised queries"
    )
    findings = agent._parse_findings(text, round=1)
    assert len(findings) == 1
    f = findings[0]
    assert f.title == "SQL injection in query"
    assert f.detail == "Unsanitized input at line 5"
    assert f.impact == "Critical"
    assert f.proposal == "Use parameterised queries"
    assert f.round_num == 1


@pytest.mark.asyncio
async def test_parse_multiple_findings():
    """Multiple findings separated by blank lines are all parsed."""
    agent = CriticAgent()
    text = (
        "FINDING: First issue\n"
        "··· Detail: Detail 1\n"
        "··· Impact: High\n"
        "··· Proposal: Fix 1\n"
        "\n"
        "FINDING: Second issue\n"
        "··· Detail: Detail 2\n"
        "··· Impact: Medium\n"
        "··· Proposal: Fix 2"
    )
    findings = agent._parse_findings(text, round=1)
    assert len(findings) == 2


@pytest.mark.asyncio
async def test_normalize_impact():
    """Impact normalization maps variations to canonical English values."""
    agent = CriticAgent()
    assert agent._normalize_impact("Critical") == "Critical"
    assert agent._normalize_impact("CRITICAL") == "Critical"
    assert agent._normalize_impact("Crítico") == "Critical"
    assert agent._normalize_impact("High") == "High"
    assert agent._normalize_impact("MEDIUM") == "Medium"
    assert agent._normalize_impact("low priority") == "Low"
    assert agent._normalize_impact("unknown value") == "Medium"  # fallback
    assert agent._normalize_impact("") == "Medium"  # fallback


@pytest.mark.asyncio
async def test_withdrawn_finding_is_skipped():
    """Findings marked WITHDRAWN are excluded from parsed results."""
    agent = CriticAgent()
    text = (
        "WITHDRAWN: SQL injection in query\n"
        "··· Detail: No longer applicable\n"
        "··· Impact: Critical\n"
        "··· Proposal: None"
    )
    findings = agent._parse_findings(text, round=3)
    assert len(findings) == 0


# ──────────────────────────────────────────────
#  Tests – System prompt
# ──────────────────────────────────────────────


def test_system_prompt_contains_role():
    """The system prompt includes the agent's role description."""
    agent = CriticAgent()
    prompt = agent._build_system_prompt()
    assert "Inverted Pyramid" in prompt
    assert "NO_FINDINGS" in prompt
    assert "FINDING:" in prompt
    assert "··· Detail:" in prompt
    assert "··· Impact:" in prompt
    assert "··· Proposal:" in prompt
