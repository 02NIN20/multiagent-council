"""In-memory diagnostics store.

Captures the last LLM/agent errors so the frontend and operators can see
*why* an analysis returned zero findings (instead of guessing).
"""

from __future__ import annotations

import threading
import time
from typing import Any


class DiagnosticsStore:
    """Thread-safe ring buffer of recent errors."""

    def __init__(self, max_entries: int = 50) -> None:
        self._max = max_entries
        self._entries: list[dict[str, Any]] = []
        self._lock = threading.Lock()

    def record(
        self,
        component: str,
        error: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Record an error event."""
        entry = {
            "timestamp": time.time(),
            "iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "component": component,
            "error": error,
            "context": context or {},
        }
        with self._lock:
            self._entries.append(entry)
            if len(self._entries) > self._max:
                self._entries = self._entries[-self._max :]

    def latest(self, n: int = 10) -> list[dict[str, Any]]:
        """Return the most recent *n* entries (newest first)."""
        with self._lock:
            return list(reversed(self._entries[-n:]))

    def clear(self) -> None:
        """Clear all entries."""
        with self._lock:
            self._entries = []


# Module-level singleton
diagnostics = DiagnosticsStore()
