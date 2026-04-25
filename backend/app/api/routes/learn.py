<<<<<<< HEAD
# backend/app/api/routes/learn.py

=======
>>>>>>> 7112dbfcf0f7cbb6a023bd5e7a3412fc2eb4431b
from importlib import import_module
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel

from app.services.session_store import load_session, save_session
<<<<<<< HEAD
from app.services.teaching_engine import generate_lesson
=======
>>>>>>> 7112dbfcf0f7cbb6a023bd5e7a3412fc2eb4431b

router = APIRouter(tags=["learn"])


<<<<<<< HEAD
class LearnRequest(BaseModel):
    student_id: str
    topic: str
    level: str = "beginner"


def _retrieve_chunks(topic: str, top_k: int = 3) -> list[str]:
    """
    Retrieve RAG context chunks for a topic.
    Tries rag_pipeline.retrieve() first, then falls back to retriever.invoke().
    Returns a list of plain text strings.
    """
=======
<<<<<<< HEAD
class LearnRequest(BaseModel):
    student_id: str
    topic: str
=======
def _retrieve_chunks(topic: str, top_k: int = 3) -> list[str]:
>>>>>>> 7112dbfcf0f7cbb6a023bd5e7a3412fc2eb4431b
    rag_module = import_module("app.rag.rag_pipeline")

    retrieve = getattr(rag_module, "retrieve", None)
    if callable(retrieve):
        result = retrieve(topic, top_k=top_k)
        if isinstance(result, list):
            return [str(item) for item in result[:top_k]]
        raise TypeError("rag_pipeline.retrieve() must return a list")

    retriever = getattr(rag_module, "retriever", None)
    if retriever is not None and hasattr(retriever, "invoke"):
        docs = retriever.invoke(topic)
        if not isinstance(docs, list):
            raise TypeError("rag_pipeline.retriever.invoke() must return a list")
        chunks: list[str] = []
        for doc in docs[:top_k]:
            content: Any = getattr(doc, "page_content", None)
            chunks.append(str(content if content is not None else doc))
        return chunks

<<<<<<< HEAD
    raise AttributeError(
        "No retrieve() function or retriever.invoke() found in app.rag.rag_pipeline"
    )


# ---------------------------------------------------------------------------
# Debug endpoints
# ---------------------------------------------------------------------------

=======
    raise AttributeError("No retrieve() function or retriever.invoke() found in app.rag.rag_pipeline")
>>>>>>> 4104795896c5f0dbeddde09d8421dec668ab50c1


>>>>>>> 7112dbfcf0f7cbb6a023bd5e7a3412fc2eb4431b
@router.get("/debug/session/{student_id}", tags=["debug"])
def debug_session(student_id: str) -> dict:
    return load_session(student_id)


@router.get("/debug/rag/{topic}", tags=["debug"])
def debug_rag(topic: str) -> dict[str, Any]:
    try:
        chunks = _retrieve_chunks(topic, top_k=3)
    except (AttributeError, ImportError, ModuleNotFoundError, TypeError, ValueError) as exc:
        return {"topic": topic, "chunks_found": 0, "chunks": [], "error": str(exc)}
    return {"topic": topic, "chunks_found": len(chunks), "chunks": chunks}


@router.get("/debug/llm", tags=["debug"])
def debug_llm() -> dict[str, Any]:
    from app.services.llm_client import call_llm

    fallback = {"test": "fallback_used"}
    return call_llm(
        prompt='Return this JSON exactly: {"test":"gemini_ok"}',
        fallback=fallback,
    )


<<<<<<< HEAD
# ---------------------------------------------------------------------------
# POST /learn — main teaching endpoint
# ---------------------------------------------------------------------------

@router.post("/learn")
def learn(req: LearnRequest) -> dict:
    session = load_session(req.student_id)

    # RAG retrieval — silently degrade if vector DB unavailable
    try:
        chunks = _retrieve_chunks(req.topic, top_k=3)
    except Exception:
        chunks = []
    context = "\n\n".join(chunks)

    # Teaching engine: Gemini → Groq → static fallback
    result = generate_lesson(req.topic, req.level, context)

    # Persist session state
    session["current_topic"] = req.topic
    session["level"] = req.level
    save_session(session)

    return result
=======
@router.post("/learn")
<<<<<<< HEAD
def learn(req: LearnRequest) -> dict:
    session = load_session(req.student_id)
    session["current_topic"] = req.topic
    save_session(session)
    return {"status": "ok", "student_id": req.student_id, "current_topic": req.topic}
=======
def learn(topic: str = "Percentage") -> dict[str, Any]:
    try:
        chunks = _retrieve_chunks(topic, top_k=3)
    except (AttributeError, ImportError, ModuleNotFoundError, TypeError, ValueError) as exc:
        return {"status": "stub", "topic": topic, "chunks_found": 0, "chunks": [], "error": str(exc)}
    return {"status": "stub", "topic": topic, "chunks_found": len(chunks), "chunks": chunks}
>>>>>>> 4104795896c5f0dbeddde09d8421dec668ab50c1
>>>>>>> 7112dbfcf0f7cbb6a023bd5e7a3412fc2eb4431b
