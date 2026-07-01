"""Base class for all tools available to agents.

Tools are stateless utility classes that agents can invoke
to perform specific actions (search code, analyze dependencies, etc.).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class BaseTool(ABC):
    """Abstract base tool."""

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        """Execute the tool with the given parameters."""
        ...
