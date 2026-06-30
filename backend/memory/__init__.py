"""Multi-level memory system for Qwen Council.

Level 1 — Working memory (volatile in-memory dict).
Level 2 — Episodic memory (PostgreSQL with forget curve).
Level 3 — Semantic memory (pgvector embeddings for consolidated patterns).
"""
