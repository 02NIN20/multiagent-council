"""Generate professional architecture diagram for Qwen Council README."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np

FIG_WIDTH = 22
FIG_HEIGHT = 14

# Colors
BG = '#1a1b26'  # dark retro bg
CARD_BG = '#24283b'
CARD_BORDER = '#3b4261'
TEXT_COLOR = '#c0caf5'
LABEL_COLOR = '#a9b1d6'
ACCENT_BLUE = '#7aa2f7'
ACCENT_GREEN = '#9ece6a'
ACCENT_RED = '#f7768e'
ACCENT_YELLOW = '#e0af68'
ACCENT_PURPLE = '#bb9af7'
ACCENT_CYAN = '#7dcfff'
ACCENT_ORANGE = '#ff9e64'

# Layer positions (y centers)
Y_FRONTEND = 12.5
Y_API = 10.5
Y_BACKEND = 8.5
Y_ORCHESTRATOR = 6.5
Y_AGENTS = 4.5
Y_SUBAGENTS = 2.5
Y_TOOLS = 0.5


def draw_card(ax, x, y, width, height, text, subtext="", color=ACCENT_BLUE, bg=CARD_BG):
    """Draw a rounded rectangle card with text."""
    box = FancyBboxPatch(
        (x - width/2, y - height/2), width, height,
        boxstyle="round,pad=0.08",
        facecolor=bg, edgecolor=color, linewidth=2,
        zorder=5,
    )
    ax.add_patch(box)
    ax.text(x, y + 0.15, text, ha='center', va='center',
            fontsize=9, fontweight='bold', color=TEXT_COLOR, zorder=6)
    if subtext:
        ax.text(x, y - 0.35, subtext, ha='center', va='center',
                fontsize=6.5, color=LABEL_COLOR, zorder=6, style='italic')


def draw_arrow(ax, x1, y1, x2, y2, color=LABEL_COLOR, style='->'):
    """Draw an arrow between two points."""
    if style == '-|>':
        arrow = FancyArrowPatch(
            (x1, y1), (x2, y2),
            arrowstyle='-|>', color=color, linewidth=1.5,
            mutation_scale=15, zorder=4,
        )
    else:
        arrow = FancyArrowPatch(
            (x1, y1), (x2, y2),
            arrowstyle='->', color=color, linewidth=1.2,
            linestyle='dashed', mutation_scale=12, zorder=4,
        )
    ax.add_patch(arrow)


def draw_layer_label(ax, y, text, color=LABEL_COLOR):
    """Draw a layer label on the left side."""
    ax.text(-0.5, y, text, ha='left', va='center',
            fontsize=10, fontweight='bold', color=color, zorder=10)


def main():
    fig, ax = plt.subplots(1, 1, figsize=(FIG_WIDTH, FIG_HEIGHT))
    ax.set_xlim(-1, 21)
    ax.set_ylim(-1, 14)
    ax.axis('off')
    ax.set_facecolor(BG)
    fig.patch.set_facecolor(BG)

    # Title
    ax.text(10, 13.7, 'Qwen Council — Agent Society Architecture',
            ha='center', va='center', fontsize=18, fontweight='bold',
            color=ACCENT_CYAN, zorder=10)
    ax.text(10, 13.2, 'Multi-Agent Collaboration System | Track 3: Agent Society',
            ha='center', va='center', fontsize=10, color=LABEL_COLOR, zorder=10)

    # ── Layer Labels ──
    draw_layer_label(ax, Y_FRONTEND, 'FRONTEND', ACCENT_PURPLE)
    draw_layer_label(ax, Y_API, 'API GATEWAY', ACCENT_YELLOW)
    draw_layer_label(ax, Y_BACKEND, 'BACKEND CORE', ACCENT_ORANGE)
    draw_layer_label(ax, Y_ORCHESTRATOR, 'ORCHESTRATOR', ACCENT_GREEN)
    draw_layer_label(ax, Y_AGENTS, 'AGENT SOCIETY', ACCENT_BLUE)
    draw_layer_label(ax, Y_SUBAGENTS, 'SUB-AGENTS', ACCENT_PURPLE)
    draw_layer_label(ax, Y_TOOLS, 'TOOLS', ACCENT_CYAN)

    # ── FRONTEND LAYER ──
    # React box
    draw_card(ax, 10, Y_FRONTEND, 12, 0.8, 'REACT FRONTEND', 'ChatGPT-style UI', ACCENT_PURPLE)
    # Features
    features = ['Sidebar\n(sessions)', 'Chat\nMessages', 'File/Image\nUpload', 'Follow-up\nQ&A']
    for i, feat in enumerate(features):
        draw_card(ax, 4 + i * 4, Y_FRONTEND - 0.9, 3.2, 0.7, feat, '', ACCENT_PURPLE)

    # Frontend → API arrow
    draw_arrow(ax, 10, Y_FRONTEND - 1.3, 10, Y_API + 0.5, ACCENT_YELLOW)

    # ── API GATEWAY ──
    api_endpoints = ['POST /api/v1/review', 'POST /api/v1/chat', 'GET /api/v1/sessions',
                     'POST .../stream', 'DELETE .../sessions/{id}', 'GET .../health']
    for i, ep in enumerate(api_endpoints):
        draw_card(ax, 3 + i * 3, Y_API, 2.6, 0.55, ep, '', ACCENT_YELLOW)

    # API → Backend arrow
    draw_arrow(ax, 10, Y_API - 0.55, 10, Y_BACKEND + 0.5, ACCENT_ORANGE)

    # ── BACKEND CORE ──
    backend_box_y = Y_BACKEND + 0.6
    # Memory System box
    draw_card(ax, 12, backend_box_y, 7, 0.7, 'MEMORY SYSTEM', '', ACCENT_ORANGE)
    mem_items = ['Working\n(in-memory)', 'Episodic\n(PostgreSQL)', 'Semantic\n(pgvector)']
    for i, mem in enumerate(mem_items):
        draw_card(ax, 9 + i * 3, backend_box_y - 0.8, 2.5, 0.6, mem, '', ACCENT_ORANGE)

    # LLM Synthesizer box
    draw_card(ax, 4, backend_box_y, 5, 0.7, 'LLM SYNTHESIZER', 'Executive Summary + Risk + Roadmap', ACCENT_ORANGE)
    draw_arrow(ax, 6.5, backend_box_y, 9, backend_box_y, ACCENT_ORANGE)

    # Backend → Orchestrator arrow
    draw_arrow(ax, 10, Y_BACKEND - 1.0, 10, Y_ORCHESTRATOR + 0.5, ACCENT_GREEN)

    # ── ORCHESTRATOR ──
    draw_card(ax, 10, Y_ORCHESTRATOR, 12, 0.7, 'COUNCIL ORCHESTRATOR', '3 debate rounds + Negotiation', ACCENT_GREEN)
    rounds = ['Round 1\nIndividual\nAnalysis', 'Round 2\nCross-Debate\n(Given-New)', 'Round 3\nFinal\nRefinement', 'Round 4\nNegotiation\n(if needed)']
    for i, rnd in enumerate(rounds):
        draw_card(ax, 3 + i * 4.8, Y_ORCHESTRATOR - 0.9, 3.8, 0.8, rnd, '', ACCENT_GREEN)

    draw_arrow(ax, 10, Y_ORCHESTRATOR - 1.3, 10, Y_AGENTS + 0.5, ACCENT_BLUE)

    # ── AGENT SOCIETY ──
    agents = [
        ('Coordinator', ACCENT_CYAN, 'Orchestrates,\ndelegates'),
        ('Analyst', ACCENT_BLUE, 'Patterns,\ncomplexity'),
        ('Architect', ACCENT_GREEN, 'Structure,\ndesign'),
        ('Engineer', ACCENT_YELLOW, 'Fixes,\noptimization'),
        ('Critic', ACCENT_RED, 'Validation,\nsecurity'),
        ('Researcher', ACCENT_PURPLE, 'Docs, best\npractices'),
    ]
    for i, (name, color, role) in enumerate(agents):
        x = 2.5 + i * 3.2
        draw_card(ax, x, Y_AGENTS, 2.8, 0.8, name, role, color)

    # Arrows from orchestrator to each agent
    for i in range(6):
        x = 2.5 + i * 3.2
        draw_arrow(ax, x, Y_AGENTS - 0.7, x, Y_SUBAGENTS + 0.5, ACCENT_PURPLE)

    # ── SUB-AGENTS ──
    subagent_groups = [
        ['TaskPlanner', 'PriorityRouter'],
        ['StaticAnalyzer', 'PatternDetector', 'ComplexityAnalyzer'],
        ['DesignPatternMatcher', 'DependencyMapper'],
        ['CodeWriter', 'Refactorer', 'Optimizer'],
        ['SecurityAuditor', 'PerformanceReviewer', 'StyleChecker'],
        ['DocGenerator', 'BestPracticeLookup'],
    ]
    for i, group in enumerate(subagent_groups):
        x_center = 2.5 + i * 3.2
        n = len(group)
        for j, sub in enumerate(group):
            x = x_center + (j - (n - 1) / 2) * 1.1
            colors = [ACCENT_CYAN, ACCENT_BLUE, ACCENT_GREEN, ACCENT_YELLOW, ACCENT_RED, ACCENT_PURPLE]
            draw_card(ax, x, Y_SUBAGENTS, 1.0, 0.4, sub, '', colors[i], '#1a1b26')

    # Arrows from sub-agents to tools
    for i in range(6):
        x = 2.5 + i * 3.2
        draw_arrow(ax, x, Y_SUBAGENTS - 0.5, x, Y_TOOLS + 0.4, ACCENT_CYAN)

    # ── TOOLS ──
    tools = ['CodeSearch\nTool', 'StaticAnalysis\nTool', 'Dependency\nAnalysis Tool', 'DocLookup\nTool']
    for i, tool in enumerate(tools):
        x = 4 + i * 4
        draw_card(ax, x, Y_TOOLS, 3.2, 0.6, tool, '', ACCENT_CYAN)

    # ── QWEN API BOTTOM BAR ──
    draw_card(ax, 10, -0.2, 20, 0.5, 'QWEN CLOUD API — dashscope-intl.aliyuncs.com — Models: qwen3-plus, qwen-vl-max, text-embedding-v3',
              '', ACCENT_CYAN, '#1a1b26')

    # Arrows from tools to Qwen API
    for i in range(4):
        x = 4 + i * 4
        draw_arrow(ax, x, Y_TOOLS - 0.3, 10, -0.45, LABEL_COLOR, '-|>')

    # Legend
    legend_x = 17.5
    legend_y = 6
    ax.text(legend_x, legend_y + 2.5, 'LEGEND', fontsize=9, fontweight='bold', color=TEXT_COLOR, zorder=10)
    legend_items = [
        ('Frontend / UI', ACCENT_PURPLE),
        ('API / Gateway', ACCENT_YELLOW),
        ('Backend Core', ACCENT_ORANGE),
        ('Orchestration', ACCENT_GREEN),
        ('Core Agents', ACCENT_BLUE),
        ('Sub-agents', ACCENT_CYAN),
        ('Data Flow', LABEL_COLOR),
    ]
    for i, (label, color) in enumerate(legend_items):
        y = legend_y + 1.8 - i * 0.5
        rect = FancyBboxPatch(
            (legend_x, y - 0.15), 0.4, 0.3,
            boxstyle="round,pad=0.02",
            facecolor=color, edgecolor=color, linewidth=1,
            zorder=5,
        )
        ax.add_patch(rect)
        ax.text(legend_x + 0.6, y, label, ha='left', va='center',
                fontsize=7, color=TEXT_COLOR, zorder=6)

    plt.tight_layout(pad=0.5)
    plt.savefig('/home/lenincoronel/Overall/alibabahack/docs/architecture_diagram.png',
                dpi=200, bbox_inches='tight', facecolor=BG, edgecolor='none')
    print("Diagram saved to docs/architecture_diagram.png")


if __name__ == '__main__':
    main()
