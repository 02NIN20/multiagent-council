"""Council agents package.

Architecture:
- Core Agents: role-based agents with sub-agents and tools
- Sub-agents: lightweight specialists delegated by core agents
- Tools: stateless utility classes for code analysis, search, etc.
"""

# Core Agents (Agent Society)
from backend.agents.core.coordinator_agent import CoordinatorAgent
from backend.agents.core.analyst_agent import AnalystAgent
from backend.agents.core.architect_agent import ArchitectAgent
from backend.agents.core.engineer_agent import EngineerAgent
from backend.agents.core.critic_agent import CriticAgent
from backend.agents.core.researcher_agent import ResearcherAgent

__all__ = [
    # Core agents (Agent Society)
    "CoordinatorAgent",
    "AnalystAgent",
    "ArchitectAgent",
    "EngineerAgent",
    "CriticAgent",
    "ResearcherAgent",
]
