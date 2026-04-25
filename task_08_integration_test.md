# Task 08 — Integration Test (Full Flow)

**Estimated time:** 30 minutes  
**Depends on:** Tasks 01–07 all complete

---

## Goal

Run the complete end-to-end flow. Verify all 4 endpoints work together correctly.

---

## No New Code Required

This task is testing only. If a test fails, fix the relevant engine task.

---

## Test Script

Save as `scripts/test_flow.sh`:

```bash
#!/bin/bash
# Full integration test for AI Tutor MVP
# Usage: bash scripts/test_flow.sh

BASE="http://localhost:8000"
STUDENT="integration_test_$(date +%s)"

echo "=== AI Tutor MVP Integration Test ==="
echo "Student ID: $STUDENT"
echo ""

# ── Step 1: /learn ──────────────────────────────────────────────────────────
echo "Step 1: POST /learn"
LEARN=$(curl -s -X POST $BASE/learn \
  -H "Content-Type: application/json" \
  -d "{\"student_id\": \"$STUDENT\", \"topic\": \"Percentage\", \"level\": \"beginner\"}")
echo "$LEARN" | python3 -m json.tool --no-ensure-ascii 2>/dev/null || echo "$LEARN"

# Validate required fields
for field in concept explanation_in_simple real_world_examples key_points step_by_step common_mistakes difficulty estimated_time_min confidence_score; do
  if echo "$LEARN" | grep -q "\"$field\""; then
    echo "  ✓ $field"
  else
    echo "  ✗ MISSING: $field"
  fi
done
echo ""

# ── Step 2: /quiz ────────────────────────────────────────────────────────────
echo "Step 2: POST /quiz"
QUIZ=$(curl -s -X POST $BASE/quiz \
  -H "Content-Type: application/json" \
  -d "{\"student_id\": \"$STUDENT\"}")
echo "$QUIZ" | python3 -m json.tool --no-ensure-ascii 2>/dev/null || echo "$QUIZ"

for field in question options answer explanation difficulty concept_tested hint time_limit_sec; do
  if echo "$QUIZ" | grep -q "\"$field\""; then
    echo "  ✓ $field"
  else
    echo "  ✗ MISSING: $field"
  fi
done

# Extract correct answer for evaluation
ANSWER=$(echo "$QUIZ" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('answer',''))" 2>/dev/null)
echo "  Correct answer: $ANSWER"
echo ""

# ── Step 3: /evaluate (correct answer) ──────────────────────────────────────
echo "Step 3: POST /evaluate (correct answer)"
EVAL=$(curl -s -X POST $BASE/evaluate \
  -H "Content-Type: application/json" \
  -d "{\"student_id\": \"$STUDENT\", \"student_answer\": \"$ANSWER\"}")
echo "$EVAL" | python3 -m json.tool --no-ensure-ascii 2>/dev/null || echo "$EVAL"

if echo "$EVAL" | grep -q '"correct": true'; then
  echo "  ✓ correct = true"
else
  echo "  ✗ expected correct = true"
fi
if echo "$EVAL" | grep -q '"score": 10'; then
  echo "  ✓ score = 10"
else
  echo "  ✗ expected score = 10"
fi
if echo "$EVAL" | grep -q '"xp_earned"'; then
  echo "  ✓ gamification.xp_earned present"
else
  echo "  ✗ gamification.xp_earned missing"
fi
echo ""

# ── Step 4: /evaluate (wrong answer) ────────────────────────────────────────
echo "Step 4: POST /evaluate (wrong answer — requires new quiz)"
curl -s -X POST $BASE/quiz \
  -H "Content-Type: application/json" \
  -d "{\"student_id\": \"$STUDENT\"}" > /dev/null

EVAL2=$(curl -s -X POST $BASE/evaluate \
  -H "Content-Type: application/json" \
  -d "{\"student_id\": \"$STUDENT\", \"student_answer\": \"DEFINITELY_WRONG_ANSWER_XYZ\"}")
echo "$EVAL2" | python3 -m json.tool --no-ensure-ascii 2>/dev/null || echo "$EVAL2"

if echo "$EVAL2" | grep -q '"correct": false'; then
  echo "  ✓ correct = false"
else
  echo "  ✗ expected correct = false"
fi
echo ""

# ── Step 5: /career ──────────────────────────────────────────────────────────
echo "Step 5: POST /career"
CAREER=$(curl -s -X POST $BASE/career \
  -H "Content-Type: application/json" \
  -d '{"goal": "SSC CGL", "completed_topics": ["Percentage"], "level": "beginner"}')
echo "$CAREER" | python3 -m json.tool --no-ensure-ascii 2>/dev/null || echo "$CAREER"

for field in recommended_roles skills_required next_steps learning_path estimated_time_months difficulty_level market_demand; do
  if echo "$CAREER" | grep -q "\"$field\""; then
    echo "  ✓ $field"
  else
    echo "  ✗ MISSING: $field"
  fi
done
echo ""

# ── Step 6: Error cases ───────────────────────────────────────────────────────
echo "Step 6: Error cases"

NO_SESSION=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE/quiz \
  -H "Content-Type: application/json" \
  -d '{"student_id": "definitely_does_not_exist_xyz123"}')
if [ "$NO_SESSION" = "404" ]; then
  echo "  ✓ /quiz without session → 404"
else
  echo "  ✗ /quiz without session → expected 404, got $NO_SESSION"
fi

NO_QUIZ=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE/evaluate \
  -H "Content-Type: application/json" \
  -d "{\"student_id\": \"$STUDENT\", \"student_answer\": \"anything\"}")
if [ "$NO_QUIZ" = "400" ]; then
  echo "  ✓ /evaluate without pending quiz → 400"
else
  echo "  ✗ /evaluate without pending quiz → expected 400, got $NO_QUIZ"
fi

echo ""
echo "=== Integration test complete ==="
```

---

## Run

```bash
# Make sure app is running
uvicorn main:app --reload &

# Run test
bash scripts/test_flow.sh
```

---

## Expected Output Summary

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
  ✓ correct = true
  ✓ score = 10
  ✓ gamification.xp_earned present

Step 4: POST /evaluate (wrong)
  ✓ correct = false

Step 5: POST /career
  ✓ recommended_roles
  ✓ skills_required
  ✓ next_steps
  ✓ learning_path
  ✓ estimated_time_months
  ✓ difficulty_level
  ✓ market_demand

Step 6: Error cases
  ✓ /quiz without session → 404
  ✓ /evaluate without pending quiz → 400

=== Integration test complete ===
```

---

## Done When

All checkmarks pass. Zero `✗` lines.
