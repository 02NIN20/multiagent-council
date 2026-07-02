# DEPRECATED: The architecture diagram is now inline Mermaid in README.md.
# This file is kept for reference only.
"""Generate professional architecture diagram using Graphviz.

Usage:
    pip install graphviz
    apt-get install graphviz  # system package for 'dot' binary
    python3 docs/generate_diagram.py
"""

from graphviz import Digraph

g = Digraph("Qwen_Council_Architecture", format="png",
            filename="docs/architecture_diagram")
g.attr(rankdir="TB", splines="ortho", bgcolor="white",
       fontname="Helvetica", nodesep="0.4", ranksep="0.6")
g.attr("node", fontname="Helvetica", fontsize="11", shape="box",
       style="rounded,filled", color="#333333")
g.attr("edge", fontname="Helvetica", fontsize="9", color="#666666")

# ── Frontend Layer ──────────────────────────────────────────────
with g.subgraph(name="cluster_frontend") as c:
    c.attr(label="REACT FRONTEND (ChatGPT-style UI)", style="rounded",
           color="#4C6EF5", fontsize="12", fontcolor="#4C6EF5")
    c.node("sidebar", "Sidebar\n(sessions)", fillcolor="#DBE4FF")
    c.node("chat", "Chat messages", fillcolor="#DBE4FF")
    c.node("upload", "File/Image\nupload", fillcolor="#DBE4FF")
    c.node("qa", "Follow-up Q&A", fillcolor="#DBE4FF")

# ── API Gateway ─────────────────────────────────────────────────
g.node("http", "HTTP (REST API)", shape="plaintext", fontsize="10")

with g.subgraph(name="cluster_backend") as c:
    c.attr(label="FASTAPI BACKEND", style="rounded",
           color="#12B886", fontsize="12", fontcolor="#12B886")
    c.node("review", "POST\n/api/v1/review", fillcolor="#C3FAE8")
    c.node("chatep", "POST\n/api/v1/chat", fillcolor="#C3FAE8")
    c.node("sessions", "GET\n/api/v1/sessions", fillcolor="#C3FAE8")

# ── Orchestrator + Memory ──────────────────────────────────────
with g.subgraph(name="cluster_orch") as c:
    c.attr(label="COUNCIL ORCHESTRATOR", style="rounded",
           color="#F08C00", fontsize="12", fontcolor="#F08C00")
    c.node("r1", "Round 1\nIndividual Analysis", fillcolor="#FFF3BF")
    c.node("r2", "Round 2\nCross-Debate", fillcolor="#FFF3BF")
    c.node("r3", "Round 3\nFinal Refinement", fillcolor="#FFF3BF")
    c.node("r4", "Round 4\nNegotiation", fillcolor="#FFF3BF")

with g.subgraph(name="cluster_memory") as c:
    c.attr(label="MEMORY SYSTEM", style="rounded",
           color="#E64980", fontsize="12", fontcolor="#E64980")
    c.node("working", "Working\n(in-memory)", fillcolor="#FFDEEB")
    c.node("episodic", "Episodic\n(PostgreSQL)", fillcolor="#FFDEEB")
    c.node("semantic", "Semantic\n(pgvector)", fillcolor="#FFDEEB")

# ── Agent Society ───────────────────────────────────────────────
with g.subgraph(name="cluster_agents") as c:
    c.attr(label="AGENT SOCIETY", style="rounded",
           color="#7048E8", fontsize="12", fontcolor="#7048E8")
    agents_list = ["Coordinator", "Analyst", "Architect",
                   "Engineer", "Critic", "Researcher"]
    for a in agents_list:
        c.node(a, a, fillcolor="#E5DBFF")

    subagents = {
        "Coordinator": ["TaskPlanner", "PrioRouter"],
        "Analyst": ["StaticAnalyzer", "Complexity"],
        "Architect": ["PatternMatcher", "DepMapper"],
        "Engineer": ["CodeWriter", "Refactorer", "Optimizer"],
        "Critic": ["SecurityAudit", "PerfReview", "StyleChecker"],
        "Researcher": ["DocGen", "BestPracLookup"],
    }
    for parent, subs in subagents.items():
        for s in subs:
            c.node(s, s, fillcolor="#F3F0FF", fontsize="9", shape="box")
            c.edge(parent, s, arrowhead="none")

    tools_list = ["CodeSearchTool", "StaticAnalysisTool",
                  "DependencyAnalysisTool", "DocLookupTool"]
    for t in tools_list:
        c.node(t, t, fillcolor="#F8F0FC", fontsize="9", shape="box3d")

    c.edge("TaskPlanner", "CodeSearchTool", style="dashed", arrowhead="none")
    c.edge("Complexity", "StaticAnalysisTool", style="dashed", arrowhead="none")
    c.edge("DepMapper", "DependencyAnalysisTool", style="dashed", arrowhead="none")
    c.edge("BestPracLookup", "DocLookupTool", style="dashed", arrowhead="none")

# ── LLM Synthesizer + Qwen API ─────────────────────────────────
g.node("synth",
       "LLM SYNTHESIZER (qwen3-plus)\n"
       "Executive Summary + Risk Overview +\n"
       "Detailed Review + Remediation Roadmap",
       fillcolor="#FFE8CC", shape="box", style="rounded,filled")

g.node("qwen",
       "QWEN CLOUD API\n"
       "https://dashscope-intl.aliyuncs.com/compatible-mode/v1\n"
       "Models: qwen3-plus, qwen-vl-max, text-embedding-v3",
       fillcolor="#FFC078", shape="box")

# ── Edges (connections) ─────────────────────────────────────────
g.edge("sidebar", "http", style="invis")
g.edge("chat", "http")
g.edge("http", "review")
g.edge("http", "chatep")
g.edge("http", "sessions")
g.edge("review", "r1")
g.edge("chatep", "working")

# Orchestrator round flow
g.edge("r1", "r2")
g.edge("r2", "r3")
g.edge("r3", "r4")
g.edge("r1", "Coordinator")
g.edge("r4", "synth")
g.edge("synth", "qwen")

# Memory ←→ Orchestrator connections
g.edge("working", "r1", style="dashed", constraint="false")
g.edge("episodic", "r4", style="dashed", constraint="false")
g.edge("semantic", "synth", style="dashed", constraint="false")

# Agents → Synthesizer
for a in agents_list:
    g.edge(a, "synth", style="invis", weight="0")

g.render(cleanup=True)
print("✅ Diagram saved to docs/architecture_diagram.png")
