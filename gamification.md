# Gamification Module

**File:** `modules/gamification.py`  
**Function:** `compute_gamification(session, correct, score) -> dict`  
**Called by:** `POST /evaluate` handler  
**Type:** Pure function — no LLM, no DB, no side effects  

---

## Rules

- Gamification is NOT an engine
- It is a single pure function
- It derives all output from quiz results + session state
- It DOES NOT have its own API endpoint
- It DOES NOT have its own database schema

---

## Allowed Outputs

| Field | Type | Notes |
|-------|------|-------|
| `xp` | int | Total cumulative XP after this answer |
| `xp_earned` | int | XP earned for this specific answer |
| `streak` | int | Consecutive correct answers in session |
| `level` | int | 1–10, computed from total XP |
| `badges` | list[str] | All badge IDs currently held |
| `badges_earned` | list[str] | Badges earned in THIS evaluation (may be empty) |

---

## NOT Allowed

- Leaderboard
- Separate `/gamification` API
- Database table for gamification
- Complex badge logic with server-side timers

---

## XP Awards

```python
XP_PER_CORRECT = 10
XP_PER_WRONG   = 0

# Streak bonus (applied if streak >= 3 after this answer)
STREAK_BONUS = {
    3:  5,   # +5 XP at streak 3
    5:  10,  # +10 XP at streak 5
    10: 20,  # +20 XP at streak 10
}
```

---

## Level Thresholds

```python
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
    10: 5000
}

def compute_level(xp: int) -> int:
    level = 1
    for lvl, threshold in XP_THRESHOLDS.items():
        if xp >= threshold:
            level = lvl
    return level
```

---

## Badge Conditions (Static)

```python
BADGE_CONDITIONS = {
    "first_lesson":  lambda session: len(session["progress"]["completed_topics"]) >= 1,
    "streak_3":      lambda session: session["gamification"]["streak"] >= 3,
    "streak_7":      lambda session: session["gamification"]["streak"] >= 7,
    "perfect_quiz":  lambda session, score: score == 10,
    "ten_topics":    lambda session: len(session["progress"]["completed_topics"]) >= 10,
}
```

---

## Full Implementation

```python
XP_PER_CORRECT = 10
XP_PER_WRONG   = 0

STREAK_BONUS = {3: 5, 5: 10, 10: 20}

XP_THRESHOLDS = {1: 0, 2: 100, 3: 250, 4: 500, 5: 900,
                 6: 1400, 7: 2000, 8: 2800, 9: 3800, 10: 5000}

def compute_level(xp: int) -> int:
    level = 1
    for lvl, threshold in XP_THRESHOLDS.items():
        if xp >= threshold:
            level = lvl
    return level

def compute_gamification(session: dict, correct: bool, score: int) -> dict:
    gami = session["gamification"]
    
    # 1. XP
    xp_earned = XP_PER_CORRECT if correct else XP_PER_WRONG
    
    # 2. Streak
    if correct:
        gami["streak"] += 1
    else:
        gami["streak"] = 0
    
    # 3. Streak bonus
    streak = gami["streak"]
    for threshold, bonus in sorted(STREAK_BONUS.items()):
        if streak == threshold:   # only on the exact streak milestone
            xp_earned += bonus
    
    # 4. Update XP
    gami["xp"] += xp_earned
    
    # 5. Level
    gami["level"] = compute_level(gami["xp"])
    
    # 6. Badges
    badges_earned = []
    
    completed_count = len(session["progress"]["completed_topics"])
    
    def award(badge_id: str, condition: bool):
        if condition and badge_id not in gami["badges"]:
            gami["badges"].append(badge_id)
            badges_earned.append(badge_id)
    
    award("first_lesson", completed_count >= 1)
    award("streak_3",     gami["streak"] >= 3)
    award("streak_7",     gami["streak"] >= 7)
    award("perfect_quiz", score == 10)
    award("ten_topics",   completed_count >= 10)
    
    return {
        "xp":           gami["xp"],
        "xp_earned":    xp_earned,
        "streak":       gami["streak"],
        "level":        gami["level"],
        "badges":       gami["badges"],
        "badges_earned": badges_earned
    }
```

---

## Example

**Input session (before):**
```json
{
  "gamification": {"xp": 90, "streak": 2, "level": 1, "badges": ["first_lesson"]},
  "progress": {"completed_topics": ["Ratio and Proportion"]}
}
```

**Call:** `compute_gamification(session, correct=True, score=10)`

**Output:**
```json
{
  "xp": 105,
  "xp_earned": 15,
  "streak": 3,
  "level": 2,
  "badges": ["first_lesson", "streak_3", "perfect_quiz"],
  "badges_earned": ["streak_3", "perfect_quiz"]
}
```

Explanation: 10 XP for correct + 5 XP streak bonus (streak hit 3). Total XP 105 → level 2 unlocked.
