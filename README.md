# 🤖 ProxyMind: Agentic Backend Core

A high-performance, secure reasoning engine for autonomous professional workflows. ProxyMind is engineered for scalability, focusing on a secure API architecture and robust data management. It serves as the **intelligent backbone** that powers autonomous agents, bridging the gap between raw LLM reasoning and production-ready infrastructure.

---

## 🧠 Vision: Semantic Memory & Autonomous Reasoning

ProxyMind's core vision is to create an AI agent that **understands context across time**. By combining LangGraph orchestration with pgvector semantic search, ProxyMind will:

- **Remember conversations semantically** — not just by keywords, but by meaning. Discuss a topic on Day 1, mention it casually on Day 7, and the agent knows exactly what you're referring to without explicit history browsing.

- **Autonomous reasoning** — The agent doesn't just retrieve memories, it reasons about them. It connects dots between past interactions and current context to make intelligent decisions about user intent and preferences.

- **Persistent agent state** — The agent evolves based on interactions, storing not just raw data but learned patterns about behavior, preferences, and conversation threads across the last 7 days.

---

## 🚀 Project Status: Foundation Phase Complete

The core infrastructure is fully functional and production-ready. The backend is secured and optimized, ready for LangGraph orchestration and semantic memory systems.

---

## ✅ Key Features (Currently Implemented)

- **FastAPI Core** — High-performance, asynchronous API endpoints designed for agentic tool-calling
- **Secure OAuth2 Auth** — JWT tokens + Argon2id password hashing
- **Agentic Memory Schema** — PostgreSQL models for storing agent context and user history
- **Type-Safe Environment** — Pydantic V2 validation for all configs
- **Database Migrations** — Alembic for safe schema versioning
- **REST API Architecture** — Clean endpoints ready for microservice integration

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Language** | Python 3.10+ |
| **Framework** | FastAPI |
| **Security** | OAuth2 (JWT) + Argon2 |
| **Database** | PostgreSQL + SQLAlchemy (Async) |
| **Validation** | Pydantic V2 |
| **Migrations** | Alembic |
| **Vector Search** | pgvector (Phase 4) |
| **Orchestration** | LangGraph (Phase 2) |

---

## 🏗️ Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| **Phase 1: Core Engine & Auth** | ✅ Complete | FastAPI, OAuth2, PostgreSQL, Alembic, REST APIs |
| **Phase 2: LangGraph Orchestration** | 📋 Next | Agent workflow management, reasoning loop, LLM tool-calling |
| **Phase 3: Memory Schema Expansion** | 📋 Planned | Semantic context capture, conversation threading, interaction patterns |
| **Phase 4: Semantic Search Layer** | 📋 Planned | pgvector embeddings, semantic search across 7-day history |
| **Phase 5: Agent Reasoning & Context** | 📋 Planned | Automatic context retrieval, intelligent responses, agent persistence |
| **Phase 6: Monitoring & Analytics** | 📋 Planned | Performance metrics, conversation analytics, memory tracking |

---

## 📦 Installation

```bash
git clone https://github.com/gitkiya/proxymind.git
cd proxymind
python -m venv venv
source venv/bin/activate # On Windows: venv\Scripts\activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app:app --reload
```

## 👤 Built by K_I_R_A_N

- Twitter: [@Kiran426578](https://twitter.com/Kiran426578)
```

