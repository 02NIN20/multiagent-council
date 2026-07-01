"""Council agents package.

Architecture:
- Core Agents: role-based agents with sub-agents and tools
- Sub-agents: lightweight specialists delegated by core agents
- Tools: stateless utility classes for code analysis, search, etc.
"""

# Core Agents (new architecture)
from backend.agents.core.coordinator_agent import CoordinatorAgent
from backend.agents.core.analyst_agent import AnalystAgent
from backend.agents.core.architect_agent import ArchitectAgent
from backend.agents.core.engineer_agent import EngineerAgent
from backend.agents.core.critic_agent import CriticAgent
from backend.agents.core.researcher_agent import ResearcherAgent

# Legacy agents (kept for backward compatibility)
from backend.agents.security_agent import SecurityAgent
from backend.agents.architecture_agent import ArchitectureAgent
from backend.agents.quality_agent import QualityAgent
from backend.agents.performance_agent import PerformanceAgent
from backend.agents.ux_agent import UXAgent
from backend.agents.vision_agent import VisionAgent

# Chat agents (old personality-based - kept for backward compatibility)
from backend.agents.scientist_agent import ScientistAgent
from backend.agents.technologist_agent import TechnologistAgent
from backend.agents.philosopher_agent import PhilosopherAgent
from backend.agents.historian_agent import HistorianAgent
from backend.agents.artist_agent import ArtistAgent
from backend.agents.psychologist_agent import PsychologistAgent
from backend.agents.strategist_agent import StrategistAgent
from backend.agents.generalist_agent import GeneralistAgent

__all__ = [
    # Core agents
    "CoordinatorAgent",
    "AnalystAgent",
    "ArchitectAgent",
    "EngineerAgent",
    "CriticAgent",
    "ResearcherAgent",
    # Legacy review agents
    "SecurityAgent",
    "ArchitectureAgent",
    "QualityAgent",
    "PerformanceAgent",
    "UXAgent",
    "VisionAgent",
    # Chat agents
    "ScientistAgent",
    "TechnologistAgent",
    "PhilosopherAgent",
    "HistorianAgent",
    "ArtistAgent",
    "PsychologistAgent",
    "StrategistAgent",
    "GeneralistAgent",
]
