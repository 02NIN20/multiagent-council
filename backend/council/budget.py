"""Token budget tracker for council reviews.

Tracks token usage across a single review session and enforces a configurable
budget. If the budget is exceeded, callers can short-circuit remaining work
(early-exit) to keep costs bounded.

The default model is ``qwen-plus-latest`` with 1M context window, so the
per-review budget is mostly a control on the *output* side and on the
*cumulative cost* across 5 agents × N rounds.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)


# Pricing for qwen-plus-latest (international / Singapore endpoint).
# USD per 1K tokens. Source: https://www.alibabacloud.com/help/en/model-studio/pricing
QWEN_PLUS_INPUT_PER_1K = 0.0008   # USD per 1K input tokens
QWEN_PLUS_OUTPUT_PER_1K = 0.002   # USD per 1K output tokens


@dataclass
class BudgetConfig:
    """Configuration for a single review's budget."""

    max_input_tokens: int = 200_000      # 200K input tokens
    max_output_tokens: int = 50_000      # 50K output tokens
    max_cost_usd: float = 1.0            # $1 per review max
    max_rounds: int = 3                  # hard cap on debate rounds

    @classmethod
    def light(cls) -> "BudgetConfig":
        """Light budget for quick reviews."""
        return cls(
            max_input_tokens=50_000,
            max_output_tokens=15_000,
            max_cost_usd=0.20,
            max_rounds=2,
        )

    @classmethod
    def full(cls) -> "BudgetConfig":
        """Full budget for thorough reviews."""
        return cls(
            max_input_tokens=200_000,
            max_output_tokens=50_000,
            max_cost_usd=1.0,
            max_rounds=3,
        )

    @classmethod
    def from_mode(cls, mode: str) -> "BudgetConfig":
        """Build a budget from a request mode ('light' or 'full')."""
        if mode == "light":
            return cls.light()
        return cls.full()


@dataclass
class TokenUsage:
    """Token usage for a single LLM call."""

    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0

    @classmethod
    def from_response(cls, response: Any) -> "TokenUsage":
        """Build TokenUsage from an OpenAI-style response with .usage."""
        usage = getattr(response, "usage", None)
        if not usage:
            return cls()
        input_t = getattr(usage, "prompt_tokens", 0) or 0
        output_t = getattr(usage, "completion_tokens", 0) or 0
        cost = (input_t / 1000) * QWEN_PLUS_INPUT_PER_1K + (output_t / 1000) * QWEN_PLUS_OUTPUT_PER_1K
        return cls(input_tokens=input_t, output_tokens=output_t, cost_usd=cost)


class TokenBudget:
    """Thread-safe (single-task) budget tracker for a single review session."""

    def __init__(self, config: BudgetConfig) -> None:
        self.config = config
        self.total_input = 0
        self.total_output = 0
        self.total_cost = 0.0
        self.call_count = 0
        self._per_call: list[dict[str, Any]] = []

    def record(self, usage: TokenUsage, label: str = "") -> None:
        """Record a single LLM call's usage."""
        self.total_input += usage.input_tokens
        self.total_output += usage.output_tokens
        self.total_cost += usage.cost_usd
        self.call_count += 1
        self._per_call.append(
            {
                "label": label,
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
                "cost_usd": round(usage.cost_usd, 6),
            }
        )

    def is_exhausted(self) -> bool:
        """Return True if the budget is exhausted and the caller should stop."""
        if self.total_input > self.config.max_input_tokens:
            logger.warning(
                "Token budget exhausted: input %d > max %d",
                self.total_input, self.config.max_input_tokens,
            )
            return True
        if self.total_output > self.config.max_output_tokens:
            logger.warning(
                "Token budget exhausted: output %d > max %d",
                self.total_output, self.config.max_output_tokens,
            )
            return True
        if self.total_cost > self.config.max_cost_usd:
            logger.warning(
                "Token budget exhausted: cost $%.4f > max $%.2f",
                self.total_cost, self.config.max_cost_usd,
            )
            return True
        return False

    def remaining(self) -> dict[str, Any]:
        """Return remaining budget as a dict (for diagnostics)."""
        return {
            "input_remaining": max(0, self.config.max_input_tokens - self.total_input),
            "output_remaining": max(0, self.config.max_output_tokens - self.total_output),
            "cost_remaining": round(max(0.0, self.config.max_cost_usd - self.total_cost), 6),
        }

    def summary(self) -> dict[str, Any]:
        """Return a full budget summary for the final report."""
        return {
            "config": {
                "max_input_tokens": self.config.max_input_tokens,
                "max_output_tokens": self.config.max_output_tokens,
                "max_cost_usd": self.config.max_cost_usd,
                "max_rounds": self.config.max_rounds,
            },
            "used": {
                "input_tokens": self.total_input,
                "output_tokens": self.total_output,
                "cost_usd": round(self.total_cost, 6),
                "call_count": self.call_count,
            },
            "exhausted": self.is_exhausted(),
            "per_call": self._per_call,
        }
