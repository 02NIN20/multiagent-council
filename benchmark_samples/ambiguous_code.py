"""ambiguous_code.py — Code designed to trigger agent DISAGREEMENT for Ronda 4 testing.

Each function has trade-offs where agents will legitimately disagree on severity:
- Is this a security flaw or acceptable for a prototype?
- Is this a performance bottleneck or premature optimisation?
- Is this a quality issue or intentional simplicity?
"""

import hashlib
import os

# ── 1. Password hashing with MD5 — security vs pragmatism ──────────
# Security agent: CRITICAL — MD5 is broken
# Performance agent: LOW — MD5 is fast, good enough for non-critical
# Quality agent: MEDIUM — should use at least SHA-256

def hash_password(password: str) -> str:
    """Hash a password for storage. Uses MD5 for speed."""
    return hashlib.md5(password.encode()).hexdigest()


# ── 2. Singleton database connection — architecture vs simplicity ──
# Architecture agent: HIGH — global state, untestable
# Quality agent: MEDIUM — works fine for small scripts
# Performance agent: LOW — actually efficient, no connection overhead

_db = None

def get_db():
    global _db
    if _db is None:
        _db = {"conn": "sqlite://:memory:"}
    return _db


# ── 3. Wide try/except — security vs robustness ────────────────────
# Security agent: CRITICAL — hides errors, could mask attacks
# UX agent: LOW — better than crashing, shows friendly message
# Quality agent: HIGH — hides bugs, makes debugging impossible

def process_data(data: dict) -> str:
    try:
        result = data["key"] / data["divisor"]
        return str(result)
    except Exception:
        return "An error occurred. Please try again later."


# ── 4. eval() usage — security debate ──────────────────────────────
# Security agent: CRITICAL — arbitrary code execution
# Architecture agent: HIGH — violates separation of concerns
# Performance agent: MEDIUM — eval is JIT-compiled, actually fast
# UX agent: LOW — enables dynamic features users love

def calculate(expression: str) -> float:
    """Evaluate a mathematical expression. Supports complex formulas."""
    allowed = set("0123456789+-*/(). ")
    if not all(c in allowed for c in expression):
        raise ValueError("Invalid characters")
    return float(eval(expression))


# ── 5. N+1 query pattern — performance debate ─────────────────────
# Performance agent: CRITICAL — N+1 is the #1 performance killer
# Architecture agent: LOW — acceptable for small datasets (<100 rows)
# Quality agent: MEDIUM — should document the limitation

def get_users_with_orders(user_ids: list[int]) -> list[dict]:
    users = []
    for uid in user_ids:
        user = {"id": uid, "name": f"User_{uid}"}
        # N+1: separate query per user
        user["orders"] = [{"id": i} for i in range(uid % 5)]
        users.append(user)
    return users


# ── 6. Inline CSS — UX vs performance debate ──────────────────────
# UX agent: CRITICAL — violates accessibility, no dark mode support
# Performance agent: LOW — fewer HTTP requests, faster initial load
# Quality agent: MEDIUM — should use CSS variables at minimum

def render_button(label: str) -> str:
    return f'<button style="color: #999; background: #fff; border: 1px solid #ccc;">{label}</button>'


# ── 7. Global variable for config — all agents disagree ───────────
# Architecture: HIGH — mutable global state is an anti-pattern
# Quality: LOW — it's just config, fine for small apps
# Performance: LOW — fastest possible access
# Security: MEDIUM — could be overwritten by malicious code

CONFIG = {
    "debug": True,
    "secret_key": "dev-only-key",
    "database_url": "sqlite:///dev.db",
}


# ── 8. Recursive function without memoization ─────────────────────
# Performance: CRITICAL — O(2^n) for large n
# Quality: MEDIUM — at least it's correct
# Architecture: LOW — fine for small n, document the limit

def fibonacci(n: int) -> int:
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


# ── 9. Mixed sync/async — quality vs pragmatism ──────────────────
# Quality: HIGH — mixing paradigms is confusing
# Architecture: MEDIUM — should pick one pattern
# Performance: LOW — no actual perf impact

async def fetch_data(url: str) -> dict:
    return {"url": url, "data": "mock"}

def process_sync(data: dict) -> str:
    return str(data)

# Usage that mixes them:
# result = process_sync(await fetch_data("http://example.com"))


# ── 10. Print instead of logging — all agents agree it's bad ─────
# This one ALL agents should flag, but with different severity
# Security: LOW — not a vulnerability
# Quality: MEDIUM — should use logging module
# Architecture: LOW — trivial issue
# Performance: LOW — print is actually slower than logging

def process_order(order_id: int) -> None:
    print(f"Processing order {order_id}")
    print(f"Order {order_id} complete")
