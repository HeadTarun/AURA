# Copilot instructions for this repository

## Build, test, and lint commands

### Environment setup
- Root workspace uses `uv` for Python packages (`pyproject.toml` + `uv.lock`) and has Bun scripts for frontend workspace tasks.
- Backend dependency install:
  - `cd backend`
  - `uv sync`

### Build / run
- Build Docker images for the stack:
  - `docker compose build`
- Start local stack with file watching (recommended in docs):
  - `docker compose watch`
- Backend-only local run (without Docker backend service):
  - `cd backend`
  - `fastapi dev app/main.py`

### Tests
- Full backend test flow (includes pre-start checks + coverage):
  - `cd backend`
  - `uv run bash scripts/tests-start.sh`
- Single backend test:
  - `cd backend`
  - `uv run pytest tests/api/routes/test_login.py::test_get_access_token -q`
- Dockerized full stack test script:
  - `bash scripts/test.sh`

### Lint / type-check
- Run configured pre-commit hooks across repository:
  - `cd backend`
  - `uv run prek run --all-files`
- Python lint/format/type checks used by hooks:
  - `uv run ruff check --force-exclude --fix --exit-non-zero-on-fix`
  - `uv run ruff format --force-exclude --exit-non-zero-on-format`
  - `uv run mypy backend/app`
  - `uv run ty check backend/app`

### Frontend-related commands
- Root scripts (`bun run lint`, `bun run test`, SDK generation) assume a `frontend/` workspace exists.
- In this checkout, `frontend/` is not present; verify frontend files are available before running Bun workspace commands.

## High-level architecture

- The main application is a FastAPI backend under `backend/app`, exposed through:
  - versioned API routes under `settings.API_V1_STR` (default `/api/v1`) via `app.api.main.api_router`
  - an unversioned health endpoint at `/health`
- Data/auth stack:
  - SQLModel models + PostgreSQL (`backend/app/models.py`, `core/db.py`)
  - Alembic migrations run in prestart (`backend/scripts/prestart.sh`)
  - OAuth2 password flow issues JWT bearer tokens (`api/routes/login.py`, `core/security.py`)
- Docker orchestration flow:
  - `db` (Postgres) -> `prestart` (DB readiness + migrations + seed) -> `backend`
  - optional `frontend` and `proxy` in compose files
- There is a separate RAG prototype under `backend/app/rag` (Streamlit/LangChain/Chroma). It is not wired into the FastAPI API router.

## Product direction from markdown specs

- The root product spec docs (`system.md`, `api_contract.md`, `data_model.md`, `teaching_engine.md`, `quiz_engine.md`, `adaptation_engine.md`, `gamification.md`, `career.md`, `task_01`..`task_08`) describe an **AI Tutor MVP** with:
  - endpoints: `/learn`, `/quiz`, `/evaluate`, `/career`
  - adaptive learning flow: teaching -> quiz -> evaluate -> adaptation
  - `StudentSession` as the core model
  - retrieval-augmented lesson generation and JSON-structured LLM outputs
- Additional implementation-oriented docs in `files/task_*.md` describe a service-layer path under `backend/app/services` using shared `llm_client`, `session_store`, and route-per-endpoint files.
- Current live backend code is still mostly the FastAPI full-stack auth/users template; when implementing roadmap work, treat the AI Tutor markdown set as the target behavior and map it onto the existing backend structure instead of assuming those modules already exist.

## Key conventions in this codebase

- **Configuration source of truth**: backend settings load from top-level `.env` using `env_file="../.env"` in `backend/app/core/config.py`.
- **Operation IDs for OpenAPI are customized**: `main.py` uses `f"{route.tags[0]}-{route.name}"`. Keep route tags stable to avoid breaking generated clients.
- **Password handling is migration-aware**:
  - verification uses `pwdlib.verify_and_update` with Argon2 + Bcrypt configured
  - successful login can transparently upgrade legacy bcrypt hashes to argon2
  - authentication uses a constant dummy hash when user is missing to reduce timing leaks
- **Auth dependency pattern**:
  - use `SessionDep`, `TokenDep`, and `CurrentUser` from `app.api.deps`
  - privilege checks use `get_current_active_superuser`
- **CI/lint expectations**:
  - Python checks are strict (`mypy strict = true`, `ty` warnings are errors)
  - pre-commit hooks include auto-fixing ruff checks and formatting
  - backend changes can trigger frontend SDK generation via `scripts/generate-client.sh`
- **Contribution workflow** (from `CONTRIBUTING.md`):
  - significant architectural changes should start with a discussion before implementation.
