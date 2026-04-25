# Task 01 — Project Setup

**Estimated time:** 30 minutes  
**Depends on:** Nothing  
**Must be done first.**

---

## Goal

Create the FastAPI project skeleton with all required files and dependencies.

---

## Input

None. Start from scratch.

---

## Output

```
ai-tutor/
├── main.py                  ← FastAPI app with 4 empty route stubs
├── requirements.txt
├── engines/
│   ├── __init__.py
│   ├── teaching_engine.py   ← stub only
│   ├── quiz_engine.py       ← stub only
│   └── adaptation_engine.py ← stub only
├── modules/
│   ├── __init__.py
│   ├── gamification.py      ← stub only
│   └── career.py            ← stub only
├── sessions/                ← empty folder (git-ignored)
└── data/                    ← empty folder for FAISS index
```

---

## Files to Create

### requirements.txt

```
fastapi==0.111.0
uvicorn==0.29.0
anthropic==0.25.0
faiss-cpu==1.8.0
pydantic==2.7.0
numpy==1.26.4
```

### main.py (stub)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json, os

app = FastAPI(title="AI Tutor MVP")

# ── Request Models ──────────────────────────────────────────────────────────

class LearnRequest(BaseModel):
    student_id: str
    topic: str
    level: str = "beginner"

class QuizRequest(BaseModel):
    student_id: str

class EvaluateRequest(BaseModel):
    student_id: str
    student_answer: str

class CareerRequest(BaseModel):
    goal: str
    completed_topics: List[str] = []
    level: str = "beginner"

# ── Session helpers ──────────────────────────────────────────────────────────

def load_session(student_id: str) -> dict:
    path = f"sessions/{student_id}.json"
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {
        "student_id": student_id,
        "current_topic": "",
        "level": "beginner",
        "progress": {"completed_topics": []},
        "quiz_history": [],
        "gamification": {"xp": 0, "streak": 0, "level": 1, "badges": []},
        "pending_quiz": None
    }

def save_session(session: dict) -> None:
    os.makedirs("sessions", exist_ok=True)
    path = f"sessions/{session['student_id']}.json"
    with open(path, "w") as f:
        json.dump(session, f, indent=2)

# ── Routes ──────────────────────────────────────────────────────────────────

@app.post("/learn")
def learn(req: LearnRequest):
    return {"status": "stub"}

@app.post("/quiz")
def quiz(req: QuizRequest):
    return {"status": "stub"}

@app.post("/evaluate")
def evaluate(req: EvaluateRequest):
    return {"status": "stub"}

@app.post("/career")
def career(req: CareerRequest):
    return {"status": "stub"}
```

### engines/__init__.py, modules/__init__.py

Both empty files.

---

## Exact Commands

```bash
mkdir -p ai-tutor/engines ai-tutor/modules ai-tutor/sessions ai-tutor/data
cd ai-tutor
touch engines/__init__.py modules/__init__.py
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## curl Test

```bash
curl http://localhost:8000/learn \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"student_id": "test", "topic": "test"}'
```

**Expected:** `{"status": "stub"}`

---

## Done When

- `uvicorn main:app --reload` starts without error
- All 4 curl requests to stubs return `{"status": "stub"}`
- No import errors
