"""Core agent implementations.

The core agents are the main specialists in the Qwen Council:
- Coordinator: orchestrates and delegates work
- Analyst: performs comprehensive code analysis
- Architect: handles architecture design and planning
- Engineer: implements fixes and optimizations
- Critic: conducts validation and quality review
- Researcher: handles documentation and best practices

These agents each extend BaseAgent and provide specialized analysis
and proactive methods beyond the basic analyze() operation.
"""

from backend.agents.core.coordinator_agent import CoordinatorAgent
from backend.agents.core.analyst_agent import AnalystAgent
from backend.agents.core.architect_agent import ArchitectAgent
from backend.agents.core.engineer_agent import EngineerAgent
from backend.agents.core.critic_agent import CriticAgent
from backend.agents.core.researcher_agent import ResearcherAgent

__all__ = [
    "CoordinatorAgent",
    "AnalystAgent",
    "ArchitectAgent",
    "EngineerAgent",
    "CriticAgent",
    "ResearcherAgent",
]