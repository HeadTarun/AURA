import json

from app.services.session_store import load_session, save_session


def test_load_session_returns_default_when_missing(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)

    session = load_session("student_001")

    assert session == {
        "student_id": "student_001",
        "current_topic": "",
        "level": "beginner",
        "progress": {"completed_topics": []},
        "quiz_history": [],
        "gamification": {"xp": 0, "streak": 0, "level": 1, "badges": []},
        "pending_quiz": None,
    }


def test_save_and_load_round_trip(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    session = load_session("student_001")
    session["current_topic"] = "Ratio and Proportion"
    session["quiz_history"].append({"question": "q1", "correct": True, "score": 10})

    save_session(session)
    loaded = load_session("student_001")

    assert loaded["student_id"] == "student_001"
    assert loaded["current_topic"] == "Ratio and Proportion"
    assert loaded["quiz_history"] == [{"question": "q1", "correct": True, "score": 10}]


def test_save_session_strips_extra_keys_and_trims_history(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    session = load_session("student_001")
    session["quiz_history"] = [
        {"question": f"q{i}", "correct": i % 2 == 0, "score": 10 if i % 2 == 0 else 0}
        for i in range(120)
    ]
    session["unexpected"] = "drop-me"

    save_session(session)

    with open(
        tmp_path / "sessions" / "student_001.json", encoding="utf-8"
    ) as session_file:
        saved = json.load(session_file)

    assert "unexpected" not in saved
    assert len(saved["quiz_history"]) == 100
    assert saved["quiz_history"][0]["question"] == "q20"
    assert saved["quiz_history"][-1]["question"] == "q119"
    assert set(saved.keys()) == {
        "student_id",
        "current_topic",
        "level",
        "progress",
        "quiz_history",
        "gamification",
        "pending_quiz",
    }


def test_load_session_fills_missing_keys_forward_compat(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "sessions").mkdir()
    raw = {
        "student_id": "student_001",
        "current_topic": "Percentage",
    }
    with open(tmp_path / "sessions" / "student_001.json", "w", encoding="utf-8") as f:
        json.dump(raw, f)

    loaded = load_session("student_001")

    assert loaded["student_id"] == "student_001"
    assert loaded["current_topic"] == "Percentage"
    assert loaded["level"] == "beginner"
    assert loaded["progress"] == {"completed_topics": []}
    assert loaded["quiz_history"] == []
    assert loaded["gamification"] == {"xp": 0, "streak": 0, "level": 1, "badges": []}
    assert loaded["pending_quiz"] is None
