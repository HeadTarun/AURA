# HackStart 🚀

A minimal, hackathon-ready full-stack starter.

| Layer | Tech |
|---|---|
| Backend | FastAPI + SQLModel + Alembic |
| Auth | JWT Bearer tokens |
| Database | PostgreSQL 16 |
| Frontend | Next.js 16 (App Router) |
| Infra | Docker Compose |

---

## Quick Start

### ⚠️ First Run (IMPORTANT — read this)

If you are starting fresh or a teammate just cloned the repo, **always reset the database volume first** to avoid Alembic migration mismatches:

```bash
docker compose down -v
docker compose up -d --build
```

> `down -v` removes the postgres data volume so Alembic runs from a clean state.

### Subsequent runs (no DB changes)

```bash
docker compose up -d
```

---

## URLs

| Service | URL |
|---|---|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8001 |
| Swagger docs | http://localhost:8001/docs |
| Health check | http://localhost:8001/health |
| Adminer | http://localhost:8081 |

---

## Default Credentials

```
Email:    admin@example.com
Password: admin123
```

These are created automatically on first start via `initial_data.py`.

---

## Verify Everything Works

```bash
# 1. Check all containers are running
docker compose ps

# 2. Check prestart logs (must show "Superuser created" or "already exists")
docker compose logs prestart

# 3. Health check
curl http://localhost:8001/health
# → {"status":"ok"}

# 4. Get a token
curl -X POST http://localhost:8001/api/v1/login/access-token \
  -d "username=admin@example.com&password=admin123"
# → {"access_token":"...","token_type":"bearer"}

# 5. Use the token
curl http://localhost:8001/api/v1/users/me \
  -H "Authorization: Bearer <your-token>"
```

---

## API Endpoints

```
POST /api/v1/login/access-token   # Login → returns JWT
GET  /api/v1/users/me             # Get current user (requires Bearer token)
POST /api/v1/users/signup         # Register a new user (public)
GET  /health                      # Health check (no auth)
```

---

## Project Structure

```
.
├── docker-compose.yml          # ← Use this (minimal, no Traefik)
├── .env                        # Environment variables
│
├── backend/
│   ├── Dockerfile
│   ├── app/
│   │   ├── main.py             # FastAPI app + /health endpoint
│   │   ├── models.py           # User model only
│   │   ├── crud.py             # User CRUD + auth
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── login.py    # POST /login/access-token
│   │   │   │   └── users.py    # GET /me, POST /signup
│   │   ├── core/
│   │   │   ├── config.py       # Settings from .env
│   │   │   ├── security.py     # JWT + password hashing
│   │   │   └── db.py           # DB engine + superuser seed
│   │   └── alembic/versions/
│   │       └── 0001_init_user.py  # Single clean migration
│
└── frontend/
    ├── Dockerfile
    ├── .env.local              # NEXT_PUBLIC_API_URL
    └── app/
        ├── page.tsx            # Landing page
        ├── login/page.tsx      # Login form
        ├── signup/page.tsx     # Registration form
        └── dashboard/page.tsx  # Protected dashboard
```

---

## Environment Variables

Key variables in `.env`:

| Variable | Default | Description |
|---|---|---|
| `FIRST_SUPERUSER` | `admin@example.com` | Auto-created on first run |
| `FIRST_SUPERUSER_PASSWORD` | `admin123` | Change before demo! |
| `SECRET_KEY` | (set) | JWT signing key |
| `POSTGRES_PASSWORD` | `root` | DB password |
| `BACKEND_CORS_ORIGINS` | `http://localhost:3000,...` | Frontend origins |
| `BACKEND_PORT` | `8001` | Host port exposed for the backend container |
| `POSTGRES_HOST_PORT` | `5433` | Host port exposed for PostgreSQL |
| `ADMINER_PORT` | `8081` | Host port exposed for Adminer |

---

## Failure Drills

**Login fails immediately after start:**
```bash
docker compose logs prestart | grep -i "superuser\|error"
```

**Cannot connect to DB:**
```bash
docker compose logs db
# Check if postgres is healthy
docker compose ps
```

**Frontend can't reach backend (CORS error):**
- Ensure `BACKEND_CORS_ORIGINS` in `.env` includes `http://localhost:3000`
- Rebuild: `docker compose up -d --build`

**Migration error (relation already exists):**
```bash
docker compose down -v  # Reset volume
docker compose up -d --build
```

---

## Building a Feature

1. Add a new SQLModel table in `backend/app/models.py`
2. Generate a migration: `alembic revision --autogenerate -m "add feature"`
3. Add CRUD in `backend/app/crud.py`
4. Add route in `backend/app/api/routes/`
5. Register in `backend/app/api/main.py`
6. Call from the frontend using the stored token

---

## License

MIT
# Cluster
