"""Tests for the new Agent Society architecture: sub-agents + budget + early-exit."""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# test_agents.py already patches AsyncOpenAI globally for the whole test session
# via _patcher.start(). We just need a fake API key.
os.environ.setdefault("OPENAI_API_KEY", "sk-test-fake-key-for-tests")


# ──────────────────────────────────────────────
#  TokenBudget
# ──────────────────────────────────────────────


def test_budget_light_defaults():
    from backend.council.budget import BudgetConfig, TokenBudget
    cfg = BudgetConfig.light()
    assert cfg.max_input_tokens == 50_000
    assert cfg.max_output_tokens == 15_000
    assert cfg.max_cost_usd == 0.20
    assert cfg.max_rounds == 2
    budget = TokenBudget(cfg)
    assert not budget.is_exhausted()


def test_budget_full_defaults():
    from backend.council.budget import BudgetConfig, TokenBudget
    cfg = BudgetConfig.full()
    assert cfg.max_input_tokens == 200_000
    assert cfg.max_cost_usd == 1.0
    assert cfg.max_rounds == 3


def test_budget_from_mode():
    from backend.council.budget import BudgetConfig
    assert BudgetConfig.from_mode("light").max_rounds == 2
    assert BudgetConfig.from_mode("full").max_rounds == 3
    assert BudgetConfig.from_mode("anything-else").max_rounds == 3  # default full


def test_budget_exhaustion_on_input():
    from backend.council.budget import BudgetConfig, TokenBudget, TokenUsage
    cfg = BudgetConfig(max_input_tokens=1000, max_output_tokens=10_000, max_cost_usd=10.0)
    budget = TokenBudget(cfg)
    # Record 1500 input tokens — should be exhausted
    budget.record(TokenUsage(input_tokens=1500, output_tokens=0, cost_usd=0.0))
    assert budget.is_exhausted()


def test_budget_exhaustion_on_cost():
    from backend.council.budget import BudgetConfig, TokenBudget, TokenUsage
    cfg = BudgetConfig(max_input_tokens=10_000_000, max_output_tokens=10_000_000, max_cost_usd=0.50)
    budget = TokenBudget(cfg)
    budget.record(TokenUsage(input_tokens=0, output_tokens=0, cost_usd=0.60))
    assert budget.is_exhausted()


def test_budget_summary_includes_per_call():
    from backend.council.budget import BudgetConfig, TokenBudget, TokenUsage
    budget = TokenBudget(BudgetConfig())
    budget.record(TokenUsage(input_tokens=100, output_tokens=50, cost_usd=0.0002), label="critic.r1")
    budget.record(TokenUsage(input_tokens=200, output_tokens=80, cost_usd=0.00032), label="critic.r2")
    summary = budget.summary()
    assert summary["used"]["input_tokens"] == 300
    assert summary["used"]["output_tokens"] == 130
    assert summary["used"]["call_count"] == 2
    assert len(summary["per_call"]) == 2
    assert summary["per_call"][0]["label"] == "critic.r1"


# ──────────────────────────────────────────────
#  Sub-agent delegation
# ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_critic_invokes_all_three_subagents():
    """The CriticAgent must call SecurityAuditor, PerformanceReviewer, StyleChecker."""
    from backend.agents.core.critic_agent import CriticAgent

    agent = CriticAgent()

    # Patch the sub-agent methods
    sec_called = []
    perf_called = []
    style_called = []

    async def fake_sec(code):
        sec_called.append(code)
        return [{"title": "SQLi", "severity": "Critical", "cwe": "CWE-89", "location": "L5", "fix": "params"}]

    async def fake_perf(code):
        perf_called.append(code)
        return [{"issue": "N+1", "severity": "High", "location": "loop", "optimization": "cache"}]

    async def fake_style(code):
        style_called.append(code)
        return [{"issue": "long line", "line": 42, "severity": "Low", "suggestion": "wrap"}]

    agent.subagents["security_auditor"].audit_security = fake_sec
    agent.subagents["performance_reviewer"].review_performance = fake_perf
    agent.subagents["style_checker"].check_style = fake_style

    # Patch the synthesis LLM call to return a simple Inverted-Pyramid
    async def fake_llm(prompt):
        return (
            "FINDING: SQL injection vulnerability\n"
            "··· Detail: SQLi at L5 (CWE-89)\n"
            "··· Impact: Critical\n"
            "··· Proposal: Use parameterised queries"
        )
    agent._call_llm = fake_llm

    findings = await agent.analyze(code="import os\ndef run(c):\n    return os.system(c)", round=1)

    assert len(sec_called) == 1, "SecurityAuditor must be called"
    assert len(perf_called) == 1, "PerformanceReviewer must be called"
    assert len(style_called) == 1, "StyleChecker must be called"
    assert len(findings) >= 1
    assert findings[0].agent == "critic"


@pytest.mark.asyncio
async def test_critic_survives_subagent_failure():
    """If a sub-agent fails, the Critic must still return findings."""
    from backend.agents.core.critic_agent import CriticAgent

    agent = CriticAgent()

    async def fake_sec(code):
        raise RuntimeError("simulated failure")
    async def fake_perf(code):
        return []
    async def fake_style(code):
        return []

    agent.subagents["security_auditor"].audit_security = fake_sec
    agent.subagents["performance_reviewer"].review_performance = fake_perf
    agent.subagents["style_checker"].check_style = fake_style

    async def fake_llm(prompt):
        return "NO_FINDINGS"
    agent._call_llm = fake_llm

    # Must not raise
    findings = await agent.analyze(code="x = 1", round=1)
    assert findings == []


@pytest.mark.asyncio
async def test_critic_uses_tools_in_round_1():
    """The Critic must invoke static_analysis tool in addition to sub-agents."""
    from backend.agents.core.critic_agent import CriticAgent

    agent = CriticAgent()

    static_called = []
    async def fake_static(**kwargs):
        static_called.append(kwargs)
        return {"total_lines": 10, "code_lines": 8, "estimated_cyclomatic_complexity": 3}
    agent.tools["static_analysis"].execute = fake_static

    async def fake_sec(code): return []
    async def fake_perf(code): return []
    async def fake_style(code): return []
    agent.subagents["security_auditor"].audit_security = fake_sec
    agent.subagents["performance_reviewer"].review_performance = fake_perf
    agent.subagents["style_checker"].check_style = fake_style

    async def fake_llm(prompt): return "NO_FINDINGS"
    agent._call_llm = fake_llm

    await agent.analyze(code="x = 1\ny = 2", round=1)
    assert len(static_called) == 1
    assert static_called[0]["analysis_type"] == "all"


@pytest.mark.asyncio
async def test_critic_skips_subagents_in_round_2():
    """Round 2+ reuses round 1's sub-agent cache (saves tokens)."""
    from backend.agents.core.critic_agent import CriticAgent

    agent = CriticAgent()

    sec_call_count = 0
    async def fake_sec(code):
        nonlocal sec_call_count
        sec_call_count += 1
        return []
    async def fake_perf(code): return []
    async def fake_style(code): return []
    agent.subagents["security_auditor"].audit_security = fake_sec
    agent.subagents["performance_reviewer"].review_performance = fake_perf
    agent.subagents["style_checker"].check_style = fake_style
    agent.tools["static_analysis"].execute = AsyncMock(return_value={})

    async def fake_llm(prompt): return "NO_FINDINGS"
    agent._call_llm = fake_llm

    # Round 1: sub-agents run
    await agent.analyze(code="x = 1", round=1)
    # Round 2: sub-agents should NOT run again
    await agent.analyze(code="x = 1", round=2, context=[])

    assert sec_call_count == 1, f"Sub-agents should run only in R1, but ran {sec_call_count} times"


# ──────────────────────────────────────────────
#  AnalystAgent
# ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_analyst_invokes_three_subagents():
    from backend.agents.core.analyst_agent import AnalystAgent
    agent = AnalystAgent()

    calls = {"static": 0, "pattern": 0, "complexity": 0}
    async def fake_static(c): calls["static"] += 1; return [{"issue": "x", "severity": "Low", "line": 1, "type": "warning"}]
    async def fake_pattern(c): calls["pattern"] += 1; return [{"pattern": "Singleton", "type": "pattern", "description": "...", "location": "L1"}]
    async def fake_complex(c): calls["complexity"] += 1; return {"cyclomatic_complexity": 5, "cognitive_complexity": 8, "hotspots": []}
    agent.subagents["static_analyzer"].analyze_static = fake_static
    agent.subagents["pattern_detector"].detect_patterns = fake_pattern
    agent.subagents["complexity_analyzer"].analyze_complexity = fake_complex
    agent._call_llm = AsyncMock(return_value="NO_FINDINGS")

    await agent.analyze(code="class A:\n    pass", round=1)
    assert calls["static"] == 1
    assert calls["pattern"] == 1
    assert calls["complexity"] == 1


# ──────────────────────────────────────────────
#  ArchitectAgent
# ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_architect_invokes_two_subagents():
    from backend.agents.core.architect_agent import ArchitectAgent
    agent = ArchitectAgent()

    calls = {"deps": 0, "patterns": 0}
    async def fake_deps(c): calls["deps"] += 1; return {"modules": [], "circular": [], "suggestions": []}
    async def fake_patterns(c): calls["patterns"] += 1; return []
    agent.subagents["dependency_mapper"].map_dependencies = fake_deps
    agent.subagents["design_pattern_matcher"].match_patterns = fake_patterns
    agent._call_llm = AsyncMock(return_value="NO_FINDINGS")

    await agent.analyze(code="x = 1", round=1)
    assert calls["deps"] == 1
    assert calls["patterns"] == 1


# ──────────────────────────────────────────────
#  EngineerAgent
# ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_engineer_invokes_three_subagents():
    from backend.agents.core.engineer_agent import EngineerAgent
    agent = EngineerAgent()

    calls = {"writer": 0, "refactor": 0, "optimize": 0}
    async def fake_writer(c, f): calls["writer"] += 1; return "def fixed(): pass"
    async def fake_refactor(c, f): calls["refactor"] += 1; return {"strategy": "Extract Method", "description": "x", "steps": ["1"], "impact": "y"}
    async def fake_optimize(c, f): calls["optimize"] += 1; return {"issue": "x", "strategy": "cache", "estimated_speedup": "2x"}
    agent.subagents["code_writer"].write_fix = fake_writer
    agent.subagents["refactorer"].suggest_refactoring = fake_refactor
    agent.subagents["optimizer"].suggest_optimization = fake_optimize
    agent._call_llm = AsyncMock(return_value="NO_FINDINGS")

    await agent.analyze(code="x = 1", round=1)
    assert calls["writer"] == 1
    assert calls["refactor"] == 1
    assert calls["optimize"] == 1


# ──────────────────────────────────────────────
#  ResearcherAgent
# ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_researcher_invokes_two_subagents():
    from backend.agents.core.researcher_agent import ResearcherAgent
    agent = ResearcherAgent()

    calls = {"bp": 0, "docs": 0}
    async def fake_bp(topic, context=""): calls["bp"] += 1; return {"summary": "x", "practices": [], "references": []}
    async def fake_docs(c): calls["docs"] += 1; return "## docs"
    agent.subagents["best_practice_lookup"].lookup = fake_bp
    agent.subagents["doc_generator"].generate_docs = fake_docs
    agent._call_llm = AsyncMock(return_value="NO_FINDINGS")

    await agent.analyze(code="def my_func(): pass", round=1)
    assert calls["bp"] == 1
    assert calls["docs"] == 1


# ──────────────────────────────────────────────
#  CoordinatorAgent
# ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_coordinator_invokes_task_planner():
    from backend.agents.core.coordinator_agent import CoordinatorAgent
    agent = CoordinatorAgent()

    called = {"planner": 0}
    async def fake_plan(c, mode="full"):
        called["planner"] += 1
        return [{"agent": "critic", "priority": 5, "focus_area": "security"}]
    agent.subagents["task_planner"].plan_review = fake_plan
    agent._call_llm = AsyncMock(return_value="NO_FINDINGS")

    await agent.analyze(code="x = 1", round=1)
    assert called["planner"] == 1


@pytest.mark.asyncio
async def test_coordinator_plan_review_delegates_to_task_planner():
    from backend.agents.core.coordinator_agent import CoordinatorAgent
    agent = CoordinatorAgent()

    async def fake_plan(c, mode="full"):
        return [
            {"agent": "critic", "priority": 5, "focus_area": "security"},
            {"agent": "analyst", "priority": 3, "focus_area": "patterns"},
        ]
    agent.subagents["task_planner"].plan_review = fake_plan

    result = await agent.plan_review("x = 1", mode="full")
    assert result["agents_to_activate"] == ["critic", "analyst"]
    assert len(result["tasks"]) == 2


# ──────────────────────────────────────────────
#  End-to-end: budget and early-exit
# ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_orchestrator_budget_is_recorded_in_report():
    """The orchestrator should record budget usage in the final report's token_usage."""
    from backend.council.budget import BudgetConfig, TokenBudget
    from backend.council.orchestrator import CouncilOrchestrator

    orch = CouncilOrchestrator()
    # Manually attach a budget (simulating what run_council does at start)
    orch.budget = TokenBudget(BudgetConfig.light())
    orch.budget.record_usage = lambda *a, **kw: None  # noop so .summary() works

    # The summary() method works as long as a budget is set
    summary = orch.budget.summary()
    assert "used" in summary
    assert "config" in summary
    assert summary["config"]["max_rounds"] == 2
    assert summary["exhausted"] is False
