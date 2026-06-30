"""Level 1: Working memory — volatile in-memory storage.

Stores session data as a simple dictionary keyed by session_id.
Data is lost on process restart.
"""

from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class WorkingMemory:
    """In-memory session storage (volatile).

    Thread-safe for async access because dict operations in CPython
    are effectively atomic for single operations, but no locking is
    performed for compound read-modify-write sequences.
    """

    def __init__(self) -> None:
        self._store: dict[str, dict[str, Any]] = {}

    def get(self, session_id: str, default: Any = None) -> dict[str, Any] | None:
        """Retrieve session data by *session_id*."""
        return self._store.get(session_id, default)

    def set(self, session_id: str, data: dict[str, Any]) -> None:
        """Store or update session data."""
        existing = self._store.get(session_id, {})
        existing.update(data)
        self._store[session_id] = existing
        logger.debug("Working memory updated for session '%s'", session_id)

    def delete(self, session_id: str) -> None:
        """Remove a session from working memory."""
        self._store.pop(session_id, None)
        logger.debug("Working memory deleted for session '%s'", session_id)

    def clear(self) -> None:
        """Clear all sessions."""
        self._store.clear()
        logger.debug("Working memory cleared")

    def list_sessions(self) -> list[str]:
        """Return all active session IDs."""
        return list(self._store.keys())

    def __contains__(self, session_id: str) -> bool:
        return session_id in self._store
