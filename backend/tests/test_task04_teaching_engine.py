"""
tests/test_task04_teaching_engine.py

Task 04 — Teaching Engine: full test suite.

Runs WITHOUT Docker / Postgres / vector DB.

Covers:
  1. validate_teaching()           — unit
  2. get_teaching_fallback()       — unit
  3. generate_lesson()             — unit (call_llm mocked)
  4. POST /learn                   — integration via TestClient
  5. POST /learn fallback          — invalid LLM response → HTTP 200 + fallback JSON
  6. Session file persistence      — student_001.json written correctly
"""

import json
import os
import sys
import types
import unittest.mock as mock

import pytest

# ── Make "app" importable from backend/ ───────────────────────────────────────
BACKEND_DIR = os.path.dirname(os.path.dirname(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


# ── Stub heavy modules BEFORE any app code is imported ────────────────────────

# 1. google.generativeai  (not installed in local venv)
_genai_stub = types.ModuleType("google.generativeai")
_genai_stub.configure = lambda **kw: None
_genai_stub.GenerationConfig = mock.MagicMock()
_genai_stub.GenerativeModel = mock.MagicMock()
sys.modules.setdefault("google", types.ModuleType("google"))
sys.modules.setdefault("google.generativeai", _genai_stub)

# 2. app.rag.rag_pipeline  (needs FAISS / Chroma / heavy ML libs)
_rag_stub = types.ModuleType("app.rag.rag_pipeline")
_rag_stub.retrieve = lambda topic, top_k=3: []   # returns empty list by default
sys.modules.setdefault("app.rag.rag_pipeline", _rag_stub)

# Now import app modules safely
from app.services.teaching_engine import (          # noqa: E402
    REQUIRED_FIELDS,
    generate_lesson,
    get_teaching_fallback,
    validate_teaching,
)

# ── Helpers ──────────────────────────────────────────────────────────────────

GOOD_LESSON = {
    "concept": "A ratio compares two quantities by division",
    "explanation_in_simple": "Ratio is used to compare two or more values.",
    "real_world_examples": ["Recipe proportions", "Map scales"],
    "key_points": ["Definition", "Formula", "Application"],
    "step_by_step": ["Identify quantities", "Write ratio", "Simplify"],
    "common_mistakes": ["Wrong order", "Missing units"],
    "difficulty": "beginner",
    "estimated_time_min": 10,
    "confidence_score": 0.85,
}


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  1. validate_teaching()                                                     ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

class TestValidateTeaching:

    def test_valid_lesson_passes(self):
        assert validate_teaching(GOOD_LESSON) is True

    @pytest.mark.parametrize("field", REQUIRED_FIELDS)
    def test_missing_field_fails(self, field):
        data = {k: v for k, v in GOOD_LESSON.items() if k != field}
        assert validate_teaching(data) is False

    @pytest.mark.parametrize("bad_input", [None, [], "string", 42])
    def test_non_dict_fails(self, bad_input):
        assert validate_teaching(bad_input) is False

    @pytest.mark.parametrize("bad_diff", ["expert", "pro", "", None, 1])
    def test_invalid_difficulty_fails(self, bad_diff):
        data = {**GOOD_LESSON, "difficulty": bad_diff}
        assert validate_teaching(data) is False

    @pytest.mark.parametrize("lvl", ["beginner", "intermediate", "advanced"])
    def test_all_valid_difficulties_pass(self, lvl):
        data = {**GOOD_LESSON, "difficulty": lvl}
        assert validate_teaching(data) is True

    def test_string_estimated_time_fails(self):
        assert validate_teaching({**GOOD_LESSON, "estimated_time_min": "ten"}) is False

    def test_float_estimated_time_fails(self):
        assert validate_teaching({**GOOD_LESSON, "estimated_time_min": 10.5}) is False

    def test_string_confidence_score_fails(self):
        assert validate_teaching({**GOOD_LESSON, "confidence_score": "high"}) is False

    def test_int_confidence_score_passes(self):
        assert validate_teaching({**GOOD_LESSON, "confidence_score": 1}) is True

    def test_float_confidence_score_passes(self):
        assert validate_teaching({**GOOD_LESSON, "confidence_score": 0.5}) is True


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  2. get_teaching_fallback()                                                 ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

class TestGetTeachingFallback:

    @pytest.mark.parametrize("level", ["beginner", "intermediate", "advanced"])
    def test_returns_valid_dict_for_all_levels(self, level):
        fb = get_teaching_fallback("Ratio and Proportion", level)
        assert validate_teaching(fb) is True

    def test_concept_mentions_topic(self):
        fb = get_teaching_fallback("Percentage", "beginner")
        assert "Percentage" in fb["concept"]

    def test_difficulty_matches_level(self):
        for lvl in ("beginner", "intermediate", "advanced"):
            fb = get_teaching_fallback("Topic", lvl)
            assert fb["difficulty"] == lvl

    def test_confidence_score_is_0_5(self):
        fb = get_teaching_fallback("Anything", "beginner")
        assert fb["confidence_score"] == 0.5

    def test_estimated_time_is_10(self):
        fb = get_teaching_fallback("Anything", "beginner")
        assert fb["estimated_time_min"] == 10

    def test_all_9_fields_present(self):
        fb = get_teaching_fallback("Topic", "beginner")
        for field in REQUIRED_FIELDS:
            assert field in fb, f"Missing field: {field}"


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  3. generate_lesson()                                                       ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

class TestGenerateLesson:

    def test_empty_topic_returns_fallback(self):
        result = generate_lesson("", "beginner", "some context")
        assert validate_teaching(result) is True
        assert result["confidence_score"] == 0.5
        assert "Unknown Topic" in result["concept"]

    def test_valid_llm_response_is_returned(self):
        with mock.patch("app.services.llm_client.call_llm", return_value=GOOD_LESSON):
            result = generate_lesson("Ratio and Proportion", "beginner", "some context")
        assert result == GOOD_LESSON

    def test_invalid_llm_response_triggers_fallback(self):
        bad_response = {"garbage": True}
        with mock.patch("app.services.llm_client.call_llm", return_value=bad_response):
            result = generate_lesson("Percentage", "beginner", "")
        assert validate_teaching(result) is True
        assert result["confidence_score"] == 0.5  # fallback marker

    def test_llm_returning_wrong_difficulty_triggers_fallback(self):
        bad = {**GOOD_LESSON, "difficulty": "expert"}
        with mock.patch("app.services.llm_client.call_llm", return_value=bad):
            result = generate_lesson("Fractions", "beginner", "")
        assert result["confidence_score"] == 0.5

    def test_no_context_uses_knowledge(self):
        with mock.patch("app.services.llm_client.call_llm", return_value=GOOD_LESSON) as m:
            generate_lesson("Topic", "beginner", "")
        call_args = m.call_args[0][0]  # first positional arg = prompt
        assert "No additional context available" in call_args

    def test_context_injected_into_prompt(self):
        ctx = "Unique RAG context chunk 12345"
        with mock.patch("app.services.llm_client.call_llm", return_value=GOOD_LESSON) as m:
            generate_lesson("Topic", "beginner", ctx)
        call_args = m.call_args[0][0]
        assert ctx in call_args

    def test_never_raises_exception(self):
        with mock.patch("app.services.llm_client.call_llm", side_effect=RuntimeError("LLM down")):
            # generate_lesson itself catches via call_llm's internal try/except
            # so this should still return fallback
            result = generate_lesson("Topic", "beginner", "")
        assert isinstance(result, dict)


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  4 & 5. POST /learn integration via TestClient                              ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

@pytest.fixture(scope="module")
def client(tmp_path_factory):
    """
    Build a minimal FastAPI app with only the /learn router.
    Uses a tmp sessions dir so tests don't pollute real sessions/.
    """
    tmp_sessions = tmp_path_factory.mktemp("sessions")

    # Patch session dir before importing
    with mock.patch("app.services.session_store.SESSION_DIR", str(tmp_sessions)):
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from app.api.routes.learn import router

        app = FastAPI()
        app.include_router(router)
        yield TestClient(app), tmp_sessions


class TestPostLearnEndpoint:

    def test_valid_request_returns_200_and_all_fields(self, client):
        tc, _ = client
        with mock.patch("app.services.llm_client.call_llm", return_value=GOOD_LESSON):
            resp = tc.post("/learn", json={
                "student_id": "student_001",
                "topic": "Ratio and Proportion",
                "level": "beginner",
            })
        assert resp.status_code == 200
        body = resp.json()
        for field in REQUIRED_FIELDS:
            assert field in body, f"Missing field in response: {field}"

    def test_response_validates_successfully(self, client):
        tc, _ = client
        with mock.patch("app.services.llm_client.call_llm", return_value=GOOD_LESSON):
            resp = tc.post("/learn", json={
                "student_id": "student_001",
                "topic": "Ratio and Proportion",
                "level": "beginner",
            })
        assert validate_teaching(resp.json()) is True

    def test_invalid_llm_returns_fallback_not_500(self, client):
        """CRITICAL: bad API keys / malformed response → HTTP 200 fallback, not 500."""
        tc, _ = client
        with mock.patch("app.services.llm_client.call_llm", return_value={"bad": "data"}):
            resp = tc.post("/learn", json={
                "student_id": "s1",
                "topic": "Percentage",
                "level": "beginner",
            })
        assert resp.status_code == 200          # never 500
        assert validate_teaching(resp.json()) is True
        assert resp.json()["confidence_score"] == 0.5  # fallback marker

    def test_default_level_is_beginner(self, client):
        tc, _ = client
        with mock.patch("app.services.llm_client.call_llm", return_value=GOOD_LESSON):
            resp = tc.post("/learn", json={
                "student_id": "s2",
                "topic": "Fractions",
                # level omitted — should default to "beginner"
            })
        assert resp.status_code == 200

    def test_rag_unavailable_still_returns_200(self, client):
        """If RAG throws, lesson is still generated from general knowledge."""
        tc, _ = client
        _rag_stub.retrieve = mock.Mock(side_effect=Exception("FAISS unavailable"))
        try:
            with mock.patch("app.services.llm_client.call_llm", return_value=GOOD_LESSON):
                resp = tc.post("/learn", json={
                    "student_id": "s3",
                    "topic": "Decimals",
                    "level": "intermediate",
                })
            assert resp.status_code == 200
        finally:
            _rag_stub.retrieve = lambda topic, top_k=3: []


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  6. Session persistence                                                     ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

class TestSessionPersistence:

    def test_session_file_created_after_learn(self, client):
        tc, tmp_sessions = client
        with mock.patch("app.services.llm_client.call_llm", return_value=GOOD_LESSON):
            tc.post("/learn", json={
                "student_id": "student_001",
                "topic": "Ratio and Proportion",
                "level": "beginner",
            })
        session_file = tmp_sessions / "student_001.json"
        assert session_file.exists(), "sessions/student_001.json not created"

    def test_session_current_topic_updated(self, client):
        tc, tmp_sessions = client
        with mock.patch("app.services.llm_client.call_llm", return_value=GOOD_LESSON):
            tc.post("/learn", json={
                "student_id": "student_001",
                "topic": "Ratio and Proportion",
                "level": "beginner",
            })
        session = json.loads((tmp_sessions / "student_001.json").read_text())
        assert session["current_topic"] == "Ratio and Proportion"

    def test_session_level_updated(self, client):
        tc, tmp_sessions = client
        with mock.patch("app.services.llm_client.call_llm", return_value=GOOD_LESSON):
            tc.post("/learn", json={
                "student_id": "student_001",
                "topic": "Ratio and Proportion",
                "level": "beginner",
            })
        session = json.loads((tmp_sessions / "student_001.json").read_text())
        assert session["level"] == "beginner"

    def test_session_student_id_stored(self, client):
        tc, tmp_sessions = client
        with mock.patch("app.services.llm_client.call_llm", return_value=GOOD_LESSON):
            tc.post("/learn", json={
                "student_id": "student_001",
                "topic": "Ratio and Proportion",
                "level": "beginner",
            })
        session = json.loads((tmp_sessions / "student_001.json").read_text())
        assert session["student_id"] == "student_001"


# ╔══════════════════════════════════════════════════════════════════════════════╗
# ║  Debug endpoints smoke test                                                 ║
# ╚══════════════════════════════════════════════════════════════════════════════╝

class TestDebugEndpoints:

    def test_debug_session_returns_200(self, client):
        tc, _ = client
        resp = tc.get("/debug/session/student_001")
        assert resp.status_code == 200
        assert "student_id" in resp.json()

    def test_debug_rag_returns_200_even_on_error(self, client):
        tc, _ = client
        resp = tc.get("/debug/rag/Fractions")
        assert resp.status_code == 200
        body = resp.json()
        assert "topic" in body
        assert "chunks_found" in body

    def test_debug_llm_returns_200(self, client):
        tc, _ = client
        with mock.patch("app.services.llm_client.call_llm", return_value={"test": "gemini_ok"}):
            resp = tc.get("/debug/llm")
        assert resp.status_code == 200
