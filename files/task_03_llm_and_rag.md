# Task 03 — LLM Client + RAG Integration

**Estimated time:** 1 hour  
**Depends on:** Task 01  
**Files to create:** `backend/app/services/llm_client.py`  
**Files to reuse (DO NOT MODIFY):** `vector_db/rag_pipeline.py`

---

## Goal

1. Implement the shared `call_llm()` function (Gemini primary → Groq fallback)
2. Verify the existing RAG pipeline can be imported and called
3. Wire `rag_pipeline.retrieve()` into the `/learn` route stub for testing

---

## Part A: LLM Client

**File:** `backend/app/services/llm_client.py`  
**Function:** `call_llm(prompt, fallback, max_tokens) -> dict`

```python
# backend/app/services/llm_client.py

import os
import json
import time
import google.generativeai as genai
from groq import Groq

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
_groq_client = Groq(api_key=os.environ["GROQ_API_KEY"])

GEMINI_MODEL = "gemini-2.5-flash"
GROQ_MODEL   = "llama-3.3-70b-versatile"
TIMEOUT_SEC  = 3


def call_llm(prompt: str, fallback: dict, max_tokens: int = 1024) -> dict:
    """
    Primary: Gemini 2.5 Flash
    Fallback: Groq Llama 3.3 70B
    Final fallback: return `fallback` dict unchanged.

    Gemini is called with response_mime_type="application/json" to force JSON.
    Groq is called with response_format={"type": "json_object"}.
    Both must return the same JSON schema — enforced by each engine's validator.
    """

    # --- Attempt 1: Gemini ---
    try:
        model = genai.GenerativeModel(GEMINI_MODEL)
        start = time.monotonic()
        resp = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=max_tokens,
                response_mime_type="application/json"
            )
        )
        elapsed = time.monotonic() - start
        if elapsed > TIMEOUT_SEC:
            raise TimeoutError(f"Gemini took {elapsed:.1f}s (limit {TIMEOUT_SEC}s)")
        text = resp.text.strip()
        return json.loads(text)
    except Exception as e:
        print(f"[llm_client] Gemini failed: {e} — trying Groq")

    # --- Attempt 2: Groq ---
    try:
        resp = _groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        text = resp.choices[0].message.content.strip()
        return json.loads(text)
    except Exception as e:
        print(f"[llm_client] Groq failed: {e} — using fallback")

    return fallback
```

---

## Part B: Verify RAG Pipeline

**DO NOT MODIFY** `vector_db/rag_pipeline.py`.

Check that it exposes a `retrieve` function:

```bash
cd Cluster
python3 -c "from vector_db.rag_pipeline import retrieve; print(retrieve('Percentage', top_k=3))"
```

If the function signature differs (e.g. `query` instead of positional), note the actual signature and update the call in `learn.py` accordingly.

**Expected output:** A list of 1–3 strings (text chunks relevant to the topic).

If the RAG pipeline requires index files to be present:
```bash
# Check what data files it needs
ls vector_db/
ls data/
```

If index files are missing, run the existing build script from the repo (check `scripts/` or `vector_db/` for a setup script). Do not create a new FAISS index — reuse the existing pipeline.

---

## Part C: Add Debug Route for RAG

Add to `backend/app/api/routes/learn.py` (temporary, remove after testing):

```python
# Temporary debug route
from fastapi import APIRouter
from vector_db.rag_pipeline import retrieve

router = APIRouter()

@router.get("/debug/rag/{topic}")
def debug_rag(topic: str):
    chunks = retrieve(topic, top_k=3)
    return {"topic": topic, "chunks_found": len(chunks), "chunks": chunks}
```

```bash
curl "http://localhost:8000/debug/rag/Percentage"
```

**Expected:**
```json
{
  "topic": "Percentage",
  "chunks_found": 2,
  "chunks": ["Percentage: Percentage means per hundred...", "..."]
}
```

---

## curl Test: LLM Client

Add a temporary test route to verify `call_llm` works end-to-end:

```python
# Temporary debug route — remove after testing
@router.get("/debug/llm")
def debug_llm():
    from backend.app.services.llm_client import call_llm
    fallback = {"test": "fallback_used"}
    result = call_llm(
        prompt='Return this JSON exactly: {"test": "gemini_ok"}',
        fallback=fallback
    )
    return result
```

```bash
curl http://localhost:8000/debug/llm
```

**Expected (Gemini working):** `{"test": "gemini_ok"}`  
**Expected (Gemini down, Groq working):** `{"test": "groq_ok"}` (or similar)  
**Expected (both down):** `{"test": "fallback_used"}`  
None of these should return HTTP 500.

---

## Done When

- `call_llm(prompt, fallback)` returns valid JSON dict from Gemini or Groq
- Gemini timeout → Groq is tried automatically
- Both fail → `fallback` dict is returned, no exception raised
- `from vector_db.rag_pipeline import retrieve` works without error
- `retrieve("Percentage", top_k=3)` returns a non-empty list
