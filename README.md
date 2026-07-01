# Qwen Council — Multi-Agent Collaboration System

**Track 3: Agent Society** — [Global AI Hackathon Series with Qwen Cloud](https://qwencloud-hackathon.dev.devpost.com/)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## Track 3 Criteria Mapping

| Criterion | How Qwen Council Meets It | Evidence |
|:----------|:--------------------------|:---------|
| **Multiple agents with distinct capabilities** | 6 code review specialists + 8 personality-based agents, each with unique prompts, domains, and expertise | `backend/agents/` — 14 agent files with distinct `role_description` and `domain` |
| **Task decomposition & role assignment** | Questions classified into 8 categories (science, tech, history, philosophy, art, psychology, strategy, general) and routed to 1-3 relevant agents | `_classify_question()` + `_route_question()` in `backend/main.py` |
| **Dialogue & negotiation** | 3 debate rounds (individual → cross-debate → refinement) + Round 4 negotiation that detects severity disagreements and forces consensus | `backend/council/orchestrator.py` — `Round 4: Negotiation` |
| **Quantifiable improvement** | Multi-agent finds **10.6x more findings** than single-agent (127 vs 12), with **100% overlap coverage** + 115 unique findings | `benchmark_results.md` — `vulnerable_app.py` benchmark |

---

## What is Qwen Council?

Qwen Council is a **multi-agent collaboration system** with two modes:

### Mode 1: Code Review (Council)
6 specialised AI agents debate collaboratively to perform code review. Each agent has unique expertise (Security, Architecture, Quality, Performance, UX, Vision) and follows a structured **Inverted Pyramid communication protocol** inspired by cognitive linguistics. After 3 rounds of structured debate + a negotiation round, a final LLM-powered report is generated.

### Mode 2: General Chat (Expert Panel)
8 personality-based agents (inspired by Feynman, Torvalds, Socrates, Harari, Miyazaki, Jung, Sun Tzu, Franklin) answer any question. Each agent has a **strict domain boundary** — they decline out-of-scope questions. A router classifies the question and activates only the 1-3 most relevant agents. Responses are synthesised into a single flowing answer.

---

## Agents

### Code Review Agents (Council Mode)

| Agent | Expertise | Domain |
|:------|:----------|:-------|
| Security | OWASP Top 10, SQLi, XSS, secrets, auth flaws | Vulnerability detection |
| Architecture | SOLID, coupling, scalability, design patterns | System design quality |
| Quality | Code style, dead code, complexity, tests | Code maintainability |
| Performance | N+1 queries, caching, inefficient loops | Runtime efficiency |
| UX | Accessibility, i18n, error messages, contrast | User experience |
| Vision | Screenshot/diagram analysis (qwen-vl-plus) | Visual inspection |

### Chat Agents (Expert Panel Mode)

| Agent | Persona | Domain |
|:------|:--------|:-------|
| Scientist | Richard Feynman | Science, nature, physics |
| Technologist | Linus Torvalds | Technology, engineering, code |
| Philosopher | Socrates | Philosophy, ethics, deep questions |
| Historian | Yuval Noah Harari | History, culture, civilizations |
| Artist | Hayao Miyazaki | Art, literature, music, creativity |
| Psychologist | Carl Jung | Psychology, human mind, archetypes |
| Strategist | Sun Tzu | Strategy, business, decision-making |
| Generalist | Benjamin Franklin | General knowledge, catch-all |

---

## Architecture

```
                    REACT FRONTEND (ChatGPT-style UI)
  Sidebar (sessions) | Chat messages | File upload | Follow-up Q&A
                            |
                     HTTP (REST API)
                            |
                    FASTAPI BACKEND
  POST /api/review  |  POST /api/chat  |  GET /api/sessions
                            |
          ------------------+------------------
          |                                  |
   COUNCIL ORCHESTRATOR                MEMORY SYSTEM
   Round 1: Individual Analysis       Working (in-memory)
   Round 2: Cross-Debate              Episodic (PostgreSQL)
   Round 3: Final Refinement          Semantic (pgvector)
   Round 4: Negotiation
          |
   LLM SYNTHESIZER (qwen3-coder-plus)
   Executive Summary + Risk Overview +
   Detailed Review + Remediation Roadmap
          |
                    QWEN CLOUD API
  https://dashscope-intl.aliyuncs.com/compatible-mode/v1
  Models: qwen3-coder-plus, qwen-vl-plus, text-embedding-v3
```

---

## Benchmark Results

### vulnerable_app.py (8 lines)

| Metric | Single-Agent | Multi-Agent | Change |
|:-------|:-------------|:------------|:-------|
| Total findings | 12 | 127 | **+958.3%** |
| Categories covered | 6/6 | 6/6 | 100% overlap |
| Unique findings | 0 | 115 | +115 |
| Coverage overlap | — | 100% | All single-agent findings preserved |

### ambiguous_code.py (13 lines)

| Metric | Single-Agent | Multi-Agent | Change |
|:-------|:-------------|:------------|:-------|
| Total findings | 10 | 88 | **+780.0%** |
| Categories covered | 4/6 | 6/6 | +50% more categories |
| Avg severity score | 3.1 | 3.3 | +6.5% higher severity |
| Unique findings | 0 | 78 | +78 |

**Conclusion:** Multi-agent system finds **8.8x–10.6x more findings** than a single generalist agent, with **100% coverage overlap** and significantly more unique insights.

---

## Communication Protocol

Each agent message follows the **Inverted Pyramid** format:

```
FINDING: SQL injection vulnerability at user input handling
... Detail: src/app.py line 45: cursor.execute(f"SELECT * FROM users WHERE id = {user_input}") (CWE-89)
... Impact: Critical
... Proposal: Use parameterised queries. BEFORE: cursor.execute(f"SELECT...{user_input}") AFTER: cursor.execute("SELECT...WHERE id = ?", (user_input,))
```

In rounds 2+, agents apply **Given-New** cross-referencing:

```
FINDING: Agreeing with Security on SQL injection at line 45, I found the same pattern at line 78
... Detail: src/app.py line 78: same f-string pattern in delete_user() (CWE-89)
... Impact: Critical
... Proposal: Create a safe_query() helper that always uses parameterisation
```

---

## Memory Architecture (3 Levels + Forgetting Curve)

| Level | Storage | Content | Lifecycle |
|:------|:--------|:--------|:----------|
| Working Memory | Python dict (volatile) | Current code, round findings, debate state | Session start → end |
| Episodic Memory | PostgreSQL | Complete sessions: code, findings, votes, decisions | Last 20 active sessions, forgetting curve (-0.1/day) |
| Semantic Memory | PostgreSQL + pgvector | User preferences, learned rules, consolidated patterns | Permanent, embeddings via Qwen API |

---

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker + Docker Compose (optional, for production)
- Qwen Cloud API key

### 1. Clone & Setup

```bash
git clone https://github.com/02NIN20/qwen-council.git
cd qwen-council

# Backend
pip install -r backend/requirements.txt
cp .env.example .env
# Edit .env and set your qwen_api_key

# Frontend
cd frontend
npm install
```

### 2. Run Locally (Development)

```bash
# Terminal 1: Backend (from project root)
PYTHONPATH=. uvicorn backend.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

Open http://localhost:5173

### 3. Run with Docker (Production)

```bash
cp .env.example .env
nano .env   # Set your qwen_api_key
docker compose up --build -d
```

The frontend will be available on `http://localhost:5173` and the API on `http://localhost:8000`.

---

## API Endpoints

| Method | Endpoint | Description |
|:-------|:---------|:------------|
| `POST` | `/api/review` | Submit code for council review (supports multiple files + instructions) |
| `POST` | `/api/review/stream` | Stream review progress via Server-Sent Events |
| `POST` | `/api/chat` | General multi-agent chat (any question, routed to relevant agents) |
| `POST` | `/api/chat/stream` | Stream chat responses via Server-Sent Events |
| `GET` | `/api/sessions` | List past sessions (review + chat) |
| `GET` | `/api/sessions/{id}` | Get session details and findings |
| `DELETE` | `/api/sessions/{id}` | Delete a session |
| `GET` | `/api/memory/patterns` | Get consolidated semantic memory patterns |
| `GET` | `/api/health` | Health check |

---

## Deployment on Alibaba Cloud ECS

```bash
ssh root@your-ecs-ip
git clone https://github.com/02NIN20/qwen-council.git
cd qwen-council
cp .env.example .env
nano .env   # Set qwen_api_key
sudo bash deploy.sh
```

---

## Built for

[Global AI Hackathon Series with Qwen Cloud](https://qwencloud-hackathon.devpost.com/) — Track 3: Agent Society

---

## License

MIT
