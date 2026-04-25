# AI Tutor — MVP System

**Version:** MVP-1.0  
**Architecture:** Synchronous, single-request → single-response  
**Goal:** Demo-ready adaptive learning system. Zero ambiguity for coding agents.

---

## 1. Core Engines (EXACTLY 3)

| Engine | Role |
|--------|------|
| `teaching_engine` | RAG-grounded lesson generation |
| `quiz_engine` | Question generation + evaluation |
| `adaptation_engine` | StudentSession mutation based on quiz results |

## 2. Modules (Lightweight, NOT engines)

| Module | Role |
|--------|------|
| `gamification` | Pure function — computes XP/streak/badges from quiz results |
| `career` | Single LLM call → Career JSON |

## 3. Removed from Original System

- planning_engine → REMOVED
- retention_engine → REMOVED
- revision_engine → REMOVED
- gamification_engine → REMOVED (replaced by pure function)
- career_engine → REMOVED (replaced by single endpoint)
- Redis queues → REMOVED
- Per-student FAISS index → REMOVED (single shared index)
- Background sync jobs → REMOVED
- WebSocket / streaming → REMOVED
- SQLite + PostgreSQL dual DB → REMOVED (single in-memory StudentSession store)

---

## 4. Architecture Diagram

```
CLIENT
  │
  │ HTTPS REST
  ▼
FastAPI App
  ├── POST /learn
  │     ├── FAISS.search(topic)        ← single shared index
  │     ├── teaching_engine(topic, context, session)
  │     ├── StudentSession.save()
  │     └── return Teaching JSON
  │
  ├── POST /quiz
  │     ├── StudentSession.load()
  │     ├── quiz_engine(session)
  │     └── return Quiz JSON
  │
  ├── POST /evaluate
  │     ├── StudentSession.load()
  │     ├── evaluate_answer(answer, quiz)  ← rule-based
  │     ├── gamification(quiz_result)      ← pure function
  │     ├── adaptation_engine(session, result)
  │     ├── StudentSession.save()
  │     └── return Evaluation + Gamification JSON
  │
  └── POST /career
        ├── LLM call (no RAG)
        └── return Career JSON

STATE STORE
  └── StudentSession (Python dict in-memory, keyed by student_id)
      └── Persisted to: sessions/{student_id}.json  (flat file, no DB)

FAISS INDEX
  └── Single shared index — loaded once at startup
      └── Path: ./data/index.faiss
```

---

## 5. Execution Flow

### POST /learn
1. Load or create `StudentSession` for `student_id`
2. Retrieve context from shared FAISS index using `topic`
3. Call `teaching_engine(topic, level, context)` → Teaching JSON
4. Save `session.current_topic = topic`
5. Return Teaching JSON

### POST /quiz
1. Load `StudentSession`
2. Call `quiz_engine(session.current_topic, session.level)` → Quiz JSON
3. Store quiz in `session.pending_quiz`
4. Return Quiz JSON

### POST /evaluate
1. Load `StudentSession`
2. Compare `student_answer` to `session.pending_quiz.answer` (exact match)
3. Call `evaluate_answer()` → Evaluation JSON
4. Call `compute_gamification(result, session)` → Gamification JSON (pure function)
5. Call `adaptation_engine(session, result)` → mutates session
6. Append to `session.quiz_history`
7. Save session
8. Return Evaluation + Gamification JSON

### POST /career
1. Build prompt from `goal` + `completed_topics`
2. LLM call → Career JSON
3. Return Career JSON (no session mutation)

---

## 6. Failure Handling

| Failure | Detection | Response |
|---------|-----------|----------|
| Invalid input (missing fields) | Pydantic validation | HTTP 422 + field errors |
| LLM returns non-JSON | JSON parse fails | Retry once → use fallback JSON |
| LLM still fails after retry | Second parse fails | Return hardcoded fallback JSON (defined per engine) |
| FAISS retrieval empty | `len(chunks) == 0` | Use `topic` string as context, log warning |
| Unknown `student_id` on `/quiz` or `/evaluate` | Session not found | HTTP 404 `{"error": "session_not_found"}` |

---

## 7. LLM Call Standard (All Engines)

Every LLM call MUST follow this pattern:

```python
def call_llm(prompt: str, fallback: dict) -> dict:
    try:
        response = anthropic.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        text = response.content[0].text
        return json.loads(text)
    except (json.JSONDecodeError, Exception):
        # Retry once
        try:
            response = anthropic.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt + "\n\nRespond ONLY with valid JSON."}]
            )
            return json.loads(response.content[0].text)
        except Exception:
            return fallback
```

---

## 8. Tech Stack

| Component | Choice |
|-----------|--------|
| API Framework | FastAPI |
| LLM | Anthropic Claude (claude-3-haiku) |
| Vector Search | FAISS (faiss-cpu) |
| Session Store | JSON files at `sessions/{student_id}.json` |
| Validation | Pydantic v2 |
| Language | Python 3.11+ |

No Redis. No Celery. No PostgreSQL. No SQLite.
