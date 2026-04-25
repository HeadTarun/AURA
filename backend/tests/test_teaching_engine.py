# backend/tests/test_teaching_engine.py
"""
Task 04 — Teaching Engine tests
Tests validate_teaching(), get_teaching_fallback(), generate_lesson(),
and the POST /learn endpoint (integration).
"""

import json
import sys
import os

# ── Make sure `app` package is importable ──────────────────────────────
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.teaching_engine import (
    REQUIRED_FIELDS,
    generate_lesson,
    get_teaching_fallback,
    validate_teaching,
)

# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Unit tests — no network, no LLM                                   ║
# ╚══════════════════════════════════════════════════════════════════════╝

PASS = 0
FAIL = 0


def check(name: str, condition: bool, detail: str = ""):
    global PASS, FAIL
    if condition:
        PASS += 1
        print(f"  ✅ {name}")
    else:
        FAIL += 1
        print(f"  ❌ {name}  — {detail}")


def test_validate_teaching():
    print("\n─── validate_teaching() ───")

    good = {
        "concept": "A ratio compares two quantities by division",
        "explanation_in_simple": "Ratio is like comparing apples to oranges.",
        "real_world_examples": ["Recipes", "Maps"],
        "key_points": ["Definition", "Formula", "Applications"],
        "step_by_step": ["Step 1", "Step 2", "Step 3"],
        "common_mistakes": ["Wrong order", "Missing units"],
        "difficulty": "beginner",
        "estimated_time_min": 10,
        "confidence_score": 0.85,
    }
    check("valid data passes", validate_teaching(good))

    # Missing field
    for field in REQUIRED_FIELDS:
        bad = {k: v for k, v in good.items() if k != field}
        check(f"missing '{field}' fails", not validate_teaching(bad))

    # Bad difficulty
    bad_diff = {**good, "difficulty": "expert"}
    check("invalid difficulty fails", not validate_teaching(bad_diff))

    # Bad estimated_time_min type
    bad_time = {**good, "estimated_time_min": "ten"}
    check("string estimated_time_min fails", not validate_teaching(bad_time))

    # Bad confidence_score type
    bad_conf = {**good, "confidence_score": "high"}
    check("string confidence_score fails", not validate_teaching(bad_conf))

    # Not a dict
    check("list input fails", not validate_teaching([1, 2, 3]))
    check("None input fails", not validate_teaching(None))
    check("string input fails", not validate_teaching("hello"))

    # Edge: confidence_score as int is valid
    int_conf = {**good, "confidence_score": 1}
    check("int confidence_score passes", validate_teaching(int_conf))

    # Edge: all three valid difficulties
    for lvl in ("beginner", "intermediate", "advanced"):
        d = {**good, "difficulty": lvl}
        check(f"difficulty='{lvl}' passes", validate_teaching(d))


def test_get_teaching_fallback():
    print("\n─── get_teaching_fallback() ───")

    fb = get_teaching_fallback("Ratio and Proportion", "beginner")

    check("returns a dict", isinstance(fb, dict))
    check("has all 9 required fields", all(f in fb for f in REQUIRED_FIELDS))
    check("validates successfully", validate_teaching(fb))
    check(
        "concept mentions topic",
        "Ratio and Proportion" in fb["concept"],
    )
    check("difficulty matches level", fb["difficulty"] == "beginner")
    check("confidence_score is 0.5", fb["confidence_score"] == 0.5)
    check("estimated_time_min is 10", fb["estimated_time_min"] == 10)

    # All three levels
    for lvl in ("beginner", "intermediate", "advanced"):
        fb_lvl = get_teaching_fallback("Test", lvl)
        check(f"fallback level={lvl} validates", validate_teaching(fb_lvl))


def test_generate_lesson_empty_topic():
    print("\n─── generate_lesson(empty topic) ───")

    result = generate_lesson("", "beginner", "")
    check("returns a dict", isinstance(result, dict))
    check("has all 9 fields", all(f in result for f in REQUIRED_FIELDS))
    check("validates successfully", validate_teaching(result))
    check(
        "concept mentions 'Unknown Topic'",
        "Unknown Topic" in result["concept"],
    )
    check("confidence_score is 0.5 (fallback)", result["confidence_score"] == 0.5)


def test_generate_lesson_with_topic():
    """
    Calls the real LLM (Gemini → Groq → fallback).
    If API keys are invalid, we expect the static fallback — never an exception.
    """
    print("\n─── generate_lesson('Ratio and Proportion', 'beginner') ───")

    result = generate_lesson(
        topic="Ratio and Proportion",
        level="beginner",
        context="A ratio compares two quantities. Proportion states that two ratios are equal.",
    )
    check("returns a dict", isinstance(result, dict))
    check("has all 9 fields", all(f in result for f in REQUIRED_FIELDS))
    check("validates successfully", validate_teaching(result))
    check(
        "difficulty is 'beginner'",
        result["difficulty"] == "beginner",
    )
    check(
        "confidence_score is a number",
        isinstance(result["confidence_score"], (int, float)),
    )

    print(f"\n  📄 Response preview:")
    print(f"     concept        : {result.get('concept', '???')[:80]}")
    print(f"     difficulty     : {result.get('difficulty')}")
    print(f"     confidence     : {result.get('confidence_score')}")
    print(f"     estimated_time : {result.get('estimated_time_min')} min")
    print(f"     key_points     : {len(result.get('key_points', []))} items")

    return result


def test_generate_lesson_no_context():
    """Generate a lesson with no RAG context — should still work."""
    print("\n─── generate_lesson('Percentage', 'intermediate', no context) ───")

    result = generate_lesson("Percentage", "intermediate", "")
    check("returns a dict", isinstance(result, dict))
    check("validates successfully", validate_teaching(result))
    check("difficulty is intermediate", result["difficulty"] == "intermediate")


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Integration test — POST /learn via HTTP                            ║
# ╚══════════════════════════════════════════════════════════════════════╝

def test_post_learn_endpoint(base_url: str = "http://localhost:8001/api/v1"):
    """Hit the live POST /learn endpoint and verify the response."""
    print(f"\n─── POST {base_url}/learn (integration) ───")

    try:
        import urllib.request

        payload = json.dumps({
            "student_id": "student_001",
            "topic": "Ratio and Proportion",
            "level": "beginner",
        }).encode()

        req = urllib.request.Request(
            f"{base_url}/learn",
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read())
            status = resp.status

        check("HTTP 200", status == 200)
        check("response is dict", isinstance(body, dict))
        check("has all 9 fields", all(f in body for f in REQUIRED_FIELDS))
        check("validates successfully", validate_teaching(body))

        print(f"\n  📄 Endpoint response:")
        print(json.dumps(body, indent=2)[:600])

    except Exception as exc:
        print(f"  ⚠️  Endpoint not reachable: {exc}")
        print("     (This is expected if Docker is not running)")


def test_session_file_updated():
    """Check that sessions/student_001.json was created/updated."""
    print("\n─── Session file check ───")

    session_path = os.path.join(
        os.path.dirname(__file__), "..", "sessions", "student_001.json"
    )
    exists = os.path.exists(session_path)
    check("sessions/student_001.json exists", exists)
    if exists:
        with open(session_path, encoding="utf-8") as f:
            session = json.load(f)
        check(
            "current_topic is 'Ratio and Proportion'",
            session.get("current_topic") == "Ratio and Proportion",
        )
        check("level is 'beginner'", session.get("level") == "beginner")
        check("student_id is 'student_001'", session.get("student_id") == "student_001")


# ╔══════════════════════════════════════════════════════════════════════╗
# ║  Main runner                                                        ║
# ╚══════════════════════════════════════════════════════════════════════╝

if __name__ == "__main__":
    print("=" * 60)
    print("  Task 04 — Teaching Engine Test Suite")
    print("=" * 60)

    # Unit tests (no network needed)
    test_validate_teaching()
    test_get_teaching_fallback()
    test_generate_lesson_empty_topic()

    # LLM tests (uses real API keys if available)
    test_generate_lesson_with_topic()
    test_generate_lesson_no_context()

    # Integration tests (needs running server)
    test_post_learn_endpoint()
    test_session_file_updated()

    print("\n" + "=" * 60)
    print(f"  Results: {PASS} passed, {FAIL} failed")
    print("=" * 60)

    sys.exit(1 if FAIL > 0 else 0)
