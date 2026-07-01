"""TaskPlanner sub-agent — plans and breaks down review tasks."""

from __future__ import annotations

from typing import Any

from backend.agents.subagents.base_subagent import BaseSubAgent


class TaskPlanner(BaseSubAgent):
    """Plans review tasks, breaks down work into subtasks."""

    def __init__(self) -> None:
        super().__init__(
            name="task_planner",
            specialty="planning review tasks and breaking down complex analyses",
        )

    async def plan_review(self, code: str, mode: str = "full") -> list[dict[str, Any]]:
        """Plan which analyses to run based on code characteristics.

        Parameters
        ----------
        code : str
            Source code to review.
        mode : str
            'full' or 'light'.

        Returns
        -------
        list of task dicts with keys: agent, priority, focus_area.
        """
        if not code.strip():
            return []

        prompt = (
            f"Analyse this code and determine which analysis agents should review it.\n\n"
            f"Code:\n```\n{code[:2000]}\n```\n\n"
            f"Available agents: analyst, architect, engineer, critic, researcher\n"
            f"Mode: {mode}\n\n"
            f"Return a JSON list of tasks, each with: agent (string), priority (1-5), focus_area (string).\n"
            f"Example: [{{\"agent\": \"critic\", \"priority\": 5, \"focus_area\": \"security audit\"}}]\n"
            f"Return ONLY valid JSON, no other text."
        )

        response = await self._call_llm(
            system_prompt="You are a task planning specialist. Break down code reviews into specific analysis tasks.",
            user_prompt=prompt,
            max_tokens=1024,
            temperature=0.2,
        )

        import json
        try:
            tasks = json.loads(response)
            if isinstance(tasks, list):
                return tasks
        except (json.JSONDecodeError, TypeError):
            pass
        # Fallback: return default tasks
        return [
            {"agent": "critic", "priority": 5, "focus_area": "full review"},
            {"agent": "analyst", "priority": 4, "focus_area": "pattern analysis"},
            {"agent": "architect", "priority": 3, "focus_area": "architecture review"},
        ]
