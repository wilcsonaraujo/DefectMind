# DefectMind

**AI-powered, graph-driven intelligence for QA.**

DefectMind is a QA intelligence platform that models quality artifacts (Stories, Requirements, TestCases, BugReports, Incidents and PostMortems) as a knowledge graph in Neo4j, with semantic search powered by embeddings and an LLM-interpreted analytics module — Health Score, Quality Hotspots, Test Coverage Analysis, Knowledge Gaps, Release Readiness, Quality Risk Report and Recommendations Engine.

The artifacts that populate the graph are themselves **AI-generated**: Data Forge uses an LLM to invent Stories, Requirements, TestCases, BugReports, Incidents and PostMortems that are coherent with each other and already connected through the correct relationships, quickly producing a realistic dataset to explore every feature of the platform.

![DefectMind Dashboard](docs/screenshots/dashboard.png)

---

## Table of Contents

- [Features](#features)
- [Screenshots](#screenshots)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
  - [Via Docker Compose](#via-docker-compose-recommended)
  - [Backend locally](#backend-locally)
  - [Frontend locally](#frontend-locally)
- [Environment Variables](#environment-variables)
- [Tests and Quality](#tests-and-quality)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [License](#license)

---

## Features

**QA artifact graph** — full CRUD for Story, Requirement, TestCase, BugReport, Incident and PostMortem, with explicit relationships between them (`HAS_REQUIREMENT`, `COVERED_BY`, `FOUND`, `CAUSED`, `ROOT_CAUSE`).

**Semantic search** — search by meaning (not just keywords) using embeddings (`sentence-transformers`, 384 dimensions) and Neo4j's native vector indexes.

**Impact analysis** — graph traversal starting from an artifact to visualize everything that would be affected by a change, with configurable depth.

**Data Forge** — AI-generated QA datasets: an LLM invents realistic Stories, Requirements, TestCases, BugReports, Incidents and PostMortems, already interlinked through the correct graph relationships, in batches and in seconds — not random data, but content coherent enough to meaningfully feed the Quality Intelligence analyses.

**Quality Intelligence** — 7 analytical features with AI interpretation, always constrained to the evidence collected from the graph (no hallucination beyond the provided context):

| Feature | What it does |
| :--- | :--- |
| **Health Score** | Classifies the risk of an artifact (LOW/MEDIUM/HIGH) based on its neighborhood in the graph. |
| **Quality Hotspots** | Ranks the Stories with the highest concentration of defects across the entire graph. |
| **Test Coverage Analysis** | Computes a coverage score and identifies Requirements without a TestCase, Stories without functional coverage, and orphan TestCases. |
| **Knowledge Gaps** | Detects traceability failures: bugs without a TestCase, incidents without a postmortem, requirements without a story and vice versa. |
| **Release Readiness** | Assesses whether a set of Stories is ready for release (`READY`/`NEEDS_ATTENTION`/`NOT_READY`), with a list of blockers. |
| **Quality Risk Report** | Combines structural graph search with semantic search for similar artifacts with a history of problems. |
| **Recommendations Engine** | Generates typed, prioritized action recommendations, always with a justification. |

## Screenshots

| Dashboard | Artifacts |
| :---: | :---: |
| ![Dashboard](docs/screenshots/dashboard.png) | ![Artifacts](docs/screenshots/artifacts.png) |

| Semantic Search | Impact Analysis |
| :---: | :---: |
| ![Semantic Search](docs/screenshots/search.png) | ![Impact Analysis](docs/screenshots/impact.png) |

| Graph Explorer | Data Forge |
| :---: | :---: |
| ![Graph Explorer](docs/screenshots/graph.png) | ![Data Forge](docs/screenshots/data-forge.png) |

| Quality Intelligence | Users |
| :---: | :---: |
| ![Quality Intelligence](docs/screenshots/quality-intelligence.png) | ![Users](docs/screenshots/users.png) |

## Tech Stack

**Backend**
- [FastAPI](https://fastapi.tiangolo.com/) — REST API
- [PostgreSQL](https://www.postgresql.org/) + SQLAlchemy + Alembic — relational data (users/authentication)
- [Neo4j](https://neo4j.com/) — QA artifact graph and vector search
- [sentence-transformers](https://www.sbert.net/) (`all-MiniLM-L6-v2`) — embeddings
- JWT — authentication
- Pluggable AI providers: Gemini, DeepSeek or Groq (selectable via `AI_PROVIDER`)

**Frontend**
- [TanStack Start](https://tanstack.com/start) (React 19) — SSR + file-based routing
- [TanStack Query](https://tanstack.com/query) — data fetching and caching
- [Tailwind CSS 4](https://tailwindcss.com/) + [shadcn/ui](https://ui.shadcn.com/) (Radix) — UI
- [React Flow](https://reactflow.dev/) — impact graph visualization

**Infrastructure**
- Docker Compose — orchestrates backend, frontend, Postgres and Neo4j
- GitHub Actions — lint (`ruff`), tests (`pytest`) and Docker image builds on every push/PR to `main`

## Architecture

```
Story ──HAS_REQUIREMENT──▶ Requirement ──COVERED_BY──▶ TestCase ──FOUND──▶ BugReport ──CAUSED──▶ Incident ──ROOT_CAUSE──▶ PostMortem
```

Each artifact is a node in Neo4j with its own application-level `id` (UUID) and a 384-dimension embedding generated from its content. The backend's `quality_intelligence` module combines structural queries against this graph with calls to an LLM, always instructed to answer strictly from the collected data.

## Getting Started

### Via Docker Compose (recommended)

```bash
cp .env.example .env
# fill in .env with the credentials you want to use
docker-compose up --build
```

| Service | URL |
| :--- | :--- |
| Frontend | http://localhost:3000 |
| Backend (API) | http://localhost:8000 |
| Backend (Swagger) | http://localhost:8000/docs |
| Neo4j Browser | http://localhost:7474 |

### Backend locally

```bash
pip install -r requirements.txt
uvicorn backend.src.main:app --reload
```

> Commands run from the repository root — backend imports are rooted at `backend.src.*`.

### Frontend locally

```bash
cd frontend
npm install
npm run dev
```

## Environment Variables

Copy `.env.example` to `.env` and fill in:

| Variable | Description |
| :--- | :--- |
| `ENVIRONMENT`, `APP_NAME`, `APP_VERSION` | Application metadata |
| `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` | Postgres credentials |
| `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | JWT configuration |
| `NEO4J_URI`, `NEO4J_USER`, `NEO4J_PASSWORD` | Neo4j connection |
| `GEMINI_API_KEY` / `DEEPSEEK_API_KEY` / `GROQ_API_KEY` | Key for the chosen AI provider |
| `AI_PROVIDER` | Active provider selector (`gemini`, `deepseek` or `groq`) |
| `VITE_API_URL` | API URL used by the frontend (optional — has an automatic fallback) |

## Tests and Quality

```bash
# Backend
pytest backend/src/tests/ -v
ruff check backend/src/

# Frontend
cd frontend
npm run lint
```

Backend tests never touch a real database: required env vars are set before any project import, `get_db` is overridden with an in-memory SQLite session, and `get_neo4j_session` with a fake session.

## API Documentation

With the backend running, interactive documentation (Swagger UI) is available at `/docs`, and the OpenAPI schema at `/openapi.json`.

## Project Structure

```
DefectMind/
├── backend/
│   └── src/
│       ├── core/            # config, database, Neo4j, auth, embeddings, AI providers
│       ├── modules/         # auth, users, artifacts, data_forge, search, quality_intelligence
│       ├── infra/alembic/   # Postgres migrations
│       └── tests/           # unit and integration tests
├── frontend/
│   └── src/
│       ├── routes/          # file-based routes (TanStack Router)
│       ├── components/      # UI components (app-layout, ui/ shadcn)
│       └── lib/              # API client, i18n, utils
├── docs/
│   └── screenshots/          # screenshots used in this README
└── docker-compose.yaml
```

## License

Distributed under the [MIT](LICENSE) license.
