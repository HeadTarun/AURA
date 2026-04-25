# Task 01 — Project Setup

**Estimated time:** 1 hour  
**Depends on:** Nothing  
**Must be done first.**  
**read current structure**

---

## Goal

install dependencies, verify the existing FastAPI app starts, create the services layer skeleton.


Verify the existing structure. Identify:
- `backend/app/main.py` — FastAPI entry point
- `backend/app/api/routes/` — existing or to-be-created route files
- Existing `requirements.txt` or `pyproject.toml`

---

## Step 2: Install Dependencies

Add to `backend/requirements.txt` (merge with existing, do not replace):

```
google-generativeai==0.7.2
groq==0.9.0
pydantic==2.7.0
fastapi==0.111.0
uvicorn==0.29.0
```

**RAG dependencies** (already in repo from document-rag-chatbot integration — do not re-add):
```
# Already present: rank_bm25, faiss-cpu, numpy, sentence-transformers
```

Install:
```bash
cd backend
pip install -r requirements.txt
```

---

## Step 3: Create Services Directory

```bash
mkdir -p backend/app/services
touch backend/app/services/__init__.py
touch backend/app/services/llm_client.py
touch backend/app/services/session_store.py
touch backend/app/services/teaching_engine.py
touch backend/app/services/quiz_engine.py
touch backend/app/services/adaptation_engine.py
touch backend/app/services/gamification.py
touch backend/app/services/career.py
mkdir -p sessions
```

---

## Step 4: Create Route Files (if not already present)

```bash
mkdir -p backend/app/api/routes
touch backend/app/api/routes/__init__.py
touch backend/app/api/routes/learn.py
touch backend/app/api/routes/quiz.py
touch backend/app/api/routes/evaluate.py
touch backend/app/api/routes/career.py
```

---

## Step 5: Scaffold main.py

If `backend/app/main.py` does not already register routes, add route stubs:

```python
# backend/app/main.py  — add to existing file, do not overwrite

from fastapi import FastAPI
from backend.app.api.routes import learn, quiz, evaluate, career

app = FastAPI(title="AI Tutor MVP")

app.include_router(learn.router)
app.include_router(quiz.router)
app.include_router(evaluate.router)
app.include_router(career.router)
```

---

## Step 6: Scaffold Each Route File (Stub)

**Function to implement:** Register router with stub returning `{"status": "stub"}`

```python
# backend/app/api/routes/learn.py
from fastapi import APIRouter
router = APIRouter()

@router.post("/learn")
def learn():
    return {"status": "stub"}
```

Repeat pattern for `quiz.py`, `evaluate.py`, `career.py`.

---

## Step 7: Set Environment Variables

```bash
export GEMINI_API_KEY=your_gemini_key_here
export GROQ_API_KEY=your_groq_key_here
```

---

## curl Test

```bash
cd AURA
uvicorn backend.app.main:app --reload --port 8000

curl -X POST http://localhost:8000/learn \
  -H "Content-Type: application/json" \
  -d '{"student_id": "test", "topic": "test"}'
```

**Expected:** `{"status": "stub"}`

Repeat for `/quiz`, `/evaluate`, `/career`.

---

## Done When

- `uvicorn` starts without import errors
- All 4 endpoints return `{"status": "stub"}`
- `backend/app/services/` directory exists with 7 empty `.py` files
- `sessions/` directory exists
- Both env vars are set and accessible in the shell
