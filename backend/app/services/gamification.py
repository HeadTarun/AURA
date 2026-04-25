from typing import Any

XP_PER_CORRECT = 10
XP_PER_WRONG = 0
STREAK_BONUS = {3: 5, 5: 10, 10: 20}
XP_THRESHOLDS = {
    1: 0,
    2: 100,
    3: 250,
    4: 500,
    5: 900,
    6: 1400,
    7: 2000,
    8: 2800,
    9: 3800,
    10: 5000,
}


def compute_level(xp: int) -> int:
    level = 1
    for lvl, threshold in XP_THRESHOLDS.items():
        if xp >= threshold:
            level = lvl
    return level


def compute_gamification(
    session: dict[str, Any], correct: bool, score: int
) -> dict[str, Any]:
    gami = session.setdefault(
        "gamification", {"xp": 0, "streak": 0, "level": 1, "badges": []}
    )
    gami.setdefault("xp", 0)
    gami.setdefault("streak", 0)
    gami.setdefault("level", 1)
    gami.setdefault("badges", [])

    xp_earned = XP_PER_CORRECT if correct else XP_PER_WRONG

    if correct:
        gami["streak"] += 1
    else:
        gami["streak"] = 0

    xp_earned += STREAK_BONUS.get(gami["streak"], 0)
    gami["xp"] += xp_earned
    gami["level"] = compute_level(gami["xp"])

    badges_earned = []
    completed_count = len(
        session.setdefault("progress", {}).setdefault("completed_topics", [])
    )

    def award(badge_id: str, condition: bool) -> None:
        if condition and badge_id not in gami["badges"]:
            gami["badges"].append(badge_id)
            badges_earned.append(badge_id)

    award("first_lesson", completed_count >= 1)
    award("streak_3", gami["streak"] >= 3)
    award("streak_7", gami["streak"] >= 7)
    award("perfect_quiz", score == 10)
    award("ten_topics", completed_count >= 10)

    return {
        "xp": gami["xp"],
        "xp_earned": xp_earned,
        "streak": gami["streak"],
        "level": gami["level"],
        "badges": gami["badges"],
        "badges_earned": badges_earned,
    }
