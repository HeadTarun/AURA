# Task 08 — Integration Test (Full Flow)

**Estimated time:** 30 minutes  
**Depends on:** Tasks 01–07 all complete  
**Repo:** https://github.com/HeadTarun/Cluster.git

---

## Goal

Run the complete end-to-end flow. Verify all 4 endpoints work together correctly.  
No new application code. Testing and bug-fixing only.

---

## Pre-flight Checklist

Before running the test script, verify:

```bash
# 1. App is running
curl -s http://localhost:8000/ | head -5   # should not 404

# 2. Env vars are set
echo "Gemini: ${GEMINI_API_KEY:0:8}..."
echo "Groq:   ${GROQ_API_KEY:0:8}..."

# 3. Sessions directory exists
ls sessions/ 2>/dev/null || echo "sessions/ missing — will be created on first /learn"

# 4. RAG pipeline importable
python3 -c "from vector_db.rag_pipeline import retrieve; print('RAG OK')"
```

---

## Test Script

Save as `scripts/test_flow.sh`:

```bash
#!/bin/bash
# Full integration test for AI Tutor MVP
# Usage: bash scripts/test_flow.sh
# Requires: uvicorn running on localhost:8000, GEMINI_API_KEY and GROQ_API_KEY set

BASE="http://localhost:8000"
STUDENT="integration_test_$(date +%s)"

echo "=== AI Tutor MVP Integration Test ==="
echo "Student ID: $STUDENT"
echo "Timestamp: $(date)"
echo ""

check_field() {
  local json="$1"
  local field="$2"
  if echo "$json" | grep -q "\"$field\""; then
    echo "  ✓ $field"
  else
    echo "  ✗ MISSING: $field"
  fi
}

# ── Step 1: /learn ──────────────────────────────────────────────────────────
echo "Step 1: POST /learn"
LEARN=$(curl -s -X POST $BASE/learn \
  -H "Content-Type: application/json" \
  -d "{\"student_id\": \"$STUDENT\", \"topic\": \"Percentage\", \"level\": \"beginner\"}")
echo "$LEARN" | python3 -m json.tool --no-ensure-ascii 2>/dev/null || echo "$LEARN"

for field in concept explanation_in_simple real_world_examples key_points step_by_step common_mistakes difficulty estimated_time_min confidence_score; do
  check_field "$LEARN" "$field"
done
echo ""

# ── Step 2: /quiz ────────────────────────────────────────────────────────────
echo "Step 2: POST /quiz"
QUIZ=$(curl -s -X POST $BASE/quiz \
  -H "Content-Type: application/json" \
  -d "{\"student_id\": \"$STUDENT\"}")
echo "$QUIZ" | python3 -m json.tool --no-ensure-ascii 2>/dev/null || echo "$QUIZ"

for field in question options answer explanation difficulty concept_tested hint time_limit_sec; do
  check_field "$QUIZ" "$field"
done

ANSWER=$(echo "$QUIZ" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('answer',''))" 2>/dev/null)
echo "  Extracted correct answer: '$ANSWER'"
echo ""

# ── Step 3: /evaluate (correct answer) ──────────────────────────────────────
echo "Step 3: POST /evaluate (correct answer)"
EVAL=$(curl -s -X POST $BASE/evaluate \
  -H "Content-Type: application/json" \
  -d "{\"student_id\": \"$STUDENT\", \"student_answer\": $(echo $ANSWER | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read().strip()))')}")
echo "$EVAL" | python3 -m json.tool --no-ensure-ascii 2>/dev/null || echo "$EVAL"

if echo "$EVAL" | grep -q '"correct": true'; then
  echo "  ✓ evaluation.correct = true"
else
  echo "  ✗ expected evaluation.correct = true"
fi
if echo "$EVAL" | grep -q '"score": 10'; then
  echo "  ✓ evaluation.score = 10"
else
  echo "  ✗ expected evaluation.score = 10"
fi
if echo "$EVAL" | grep -q '"xp_earned"'; then
  echo "  ✓ gamification.xp_earned present"
else
  echo "  ✗ gamification.xp_earned missing"
fi
if echo "$EVAL" | grep -q '"badges"'; then
  echo "  ✓ gamification.badges present"
else
  echo "  ✗ gamification.badges missing"
fi
echo ""

# ── Step 4: /evaluate (wrong answer) ────────────────────────────────────────
echo "Step 4: POST /evaluate (wrong answer — requires new /quiz call first)"

curl -s -X POST $BASE/quiz \
  -H "Content-Type: application/json" \
  -d "{\"student_id\": \"$STUDENT\"}" > /dev/null

EVAL2=$(curl -s -X POST $BASE/evaluate \
  -H "Content-Type: application/json" \
  -d "{\"student_id\": \"$STUDENT\", \"student_answer\": \"DEFINITELY_WRONG_ANSWER_XYZ_12345\"}")
echo "$EVAL2" | python3 -m json.tool --no-ensure-ascii 2>/dev/null || echo "$EVAL2"

if echo "$EVAL2" | grep -q '"correct": false'; then
  echo "  ✓ evaluation.correct = false"
else
  echo "  ✗ expected evaluation.correct = false"
fi
if echo "$EVAL2" | grep -q '"score": 0'; then
  echo "  ✓ evaluation.score = 0"
else
  echo "  ✗ expected evaluation.score = 0"
fi
echo ""

# ── Step 5: /career ──────────────────────────────────────────────────────────
echo "Step 5: POST /career"
CAREER=$(curl -s -X POST $BASE/career \
  -H "Content-Type: application/json" \
  -d '{"goal": "SSC CGL", "completed_topics": ["Percentage"], "level": "beginner"}')
echo "$CAREER" | python3 -m json.tool --no-ensure-ascii 2>/dev/null || echo "$CAREER"

for field in recommended_roles skills_required next_steps learning_path estimated_time_months difficulty_level market_demand; do
  check_field "$CAREER" "$field"
done
echo ""

# ── Step 6: Error cases ───────────────────────────────────────────────────────
echo "Step 6: Error cases"

NO_SESSION_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE/quiz \
  -H "Content-Type: application/json" \
  -d '{"student_id": "definitely_does_not_exist_xyz999"}')
if [ "$NO_SESSION_CODE" = "404" ]; then
  echo "  ✓ /quiz without session → HTTP 404"
else
  echo "  ✗ /quiz without session → expected 404, got $NO_SESSION_CODE"
fi

NO_QUIZ_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE/evaluate \
  -H "Content-Type: application/json" \
  -d "{\"student_id\": \"$STUDENT\", \"student_answer\": \"anything\"}")
if [ "$NO_QUIZ_CODE" = "400" ]; then
  echo "  ✓ /evaluate without pending quiz → HTTP 400"
else
  echo "  ✗ /evaluate without pending quiz → expected 400, got $NO_QUIZ_CODE"
fi

# ── Step 7: Session file validation ─────────────────────────────────────────
echo ""
echo "Step 7: Session file validation"
SESSION_FILE="sessions/${STUDENT}.json"
if [ -f "$SESSION_FILE" ]; then
  echo "  ✓ Session file exists: $SESSION_FILE"
  python3 -c "
import json
with open('$SESSION_FILE') as f:
    s = json.load(f)
expected = {'student_id','current_topic','level','progress','quiz_history','gamification','pending_quiz'}
actual = set(s.keys())
extra = actual - expected
missing = expected - actual
if extra:
    print(f'  ✗ Extra keys found: {extra}')
else:
    print('  ✓ No extra keys in session')
if missing:
    print(f'  ✗ Missing keys: {missing}')
else:
    print('  ✓ All required keys present')
print(f'  ✓ quiz_history has {len(s[\"quiz_history\"])} entries')
print(f'  ✓ pending_quiz is: {s[\"pending_quiz\"]}')
"
else
  echo "  ✗ Session file not found: $SESSION_FILE"
fi

echo ""
echo "=== Integration test complete ==="
```

---

## Run

```bash
# Terminal 1: Start the app
cd Cluster
uvicorn backend.app.main:app --reload --port 8000

# Terminal 2: Run test
export GEMINI_API_KEY=your_key
export GROQ_API_KEY=your_key
bash scripts/test_flow.sh
```

---

## Expected Output

```
=== AI Tutor MVP Integration Test ===
Step 1: POST /learn
  ✓ concept
  ✓ explanation_in_simple
  ✓ real_world_examples
  ✓ key_points
  ✓ step_by_step
  ✓ common_mistakes
  ✓ difficulty
  ✓ estimated_time_min
  ✓ confidence_score

Step 2: POST /quiz
  ✓ question
  ✓ options
  ✓ answer
  ✓ explanation
  ✓ difficulty
  ✓ concept_tested
  ✓ hint
  ✓ time_limit_sec

Step 3: POST /evaluate (correct)
  ✓ evaluation.correct = true
  ✓ evaluation.score = 10
  ✓ gamification.xp_earned present
  ✓ gamification.badges present

Step 4: POST /evaluate (wrong)
  ✓ evaluation.correct = false
  ✓ evaluation.score = 0

Step 5: POST /career
  ✓ recommended_roles
  ✓ skills_required
  ✓ next_steps
  ✓ learning_path
  ✓ estimated_time_months
  ✓ difficulty_level
  ✓ market_demand

Step 6: Error cases
  ✓ /quiz without session → HTTP 404
  ✓ /evaluate without pending quiz → HTTP 400

Step 7: Session file validation
  ✓ Session file exists
  ✓ No extra keys in session
  ✓ All required keys present
  ✓ quiz_history has 2 entries
  ✓ pending_quiz is: None

=== Integration test complete ===
```

---

## Common Failures and Fixes

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| `✗ concept` missing | Teaching engine returning fallback | Check `GEMINI_API_KEY` is valid |
| `✗ evaluation.correct = true` | Answer comparison failing | Check answer extracted correctly from step 2 |
| `✗ /quiz without session → 404` | Route returning wrong status | Check HTTPException status_code in `quiz.py` |
| `✗ Extra keys in session` | `save_session` not stripping keys | Verify `ALLOWED_KEYS` logic in `session_store.py` |
| `from vector_db.rag_pipeline import retrieve` fails | RAG index not built | Run repo's existing setup script in `vector_db/` |

---

## Done When

All checkmarks pass. Zero `✗` lines.
