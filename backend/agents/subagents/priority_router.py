"""PriorityRouter sub-agent — routes tasks based on urgency and importance."""

from __future__ import annotations

from typing import Any

from backend.agents.subagents.base_subagent import BaseSubAgent


class PriorityRouter(BaseSubAgent):
    """Routes tasks to appropriate agents based on priority and code context."""

    def __init__(self) -> None:
        super().__init__(
            name="priority_router",
            specialty="routing tasks based on urgency and code characteristics",
        )

    async def route_tasks(self, findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Route findings to appropriate agents for follow-up.

        Parameters
        ----------
        findings : list[dict]
            Findings to route.

        Returns
        -------
        list of routed tasks with keys: finding, target_agent, action.
        """
        if not findings:
            return []

        # Route based on impact and agent
        routed = []
        for f in findings:
            impact = f.get("impact", "Medium")
            agent = f.get("agent", "unknown")

            # Critical findings go to engineer for fix
            if impact == "Critical":
                routed.append({"finding": f, "target_agent": "engineer", "action": "implement_fix"})
            # Security findings go to critic for deeper audit
            elif "security" in (f.get("title", "") + f.get("detail", "")).lower():
                routed.append({"finding": f, "target_agent": "critic", "action": "security_audit"})
            # Performance findings go to engineer for optimization
            elif "performance" in (f.get("title", "") + f.get("detail", "")).lower():
                routed.append({"finding": f, "target_agent": "engineer", "action": "optimize"})
            # Architecture findings go to architect
            elif agent == "architect" or "architecture" in (f.get("title", "") + f.get("detail", "")).lower():
                routed.append({"finding": f, "target_agent": "architect", "action": "plan_refactor"})
            # Default: route back to same agent for refinement
            else:
                routed.append({"finding": f, "target_agent": agent, "action": "review"})

        return routed
