# Task 03 — FAISS Index Setup

**Estimated time:** 45 minutes  
**Depends on:** Task 01

---

## Goal

Build a single shared FAISS index from a sample text file. Implement `faiss_search(topic) -> list[str]`. Load the index once at app startup.

---

## Input

A plain text file at `data/syllabus.txt` — one paragraph per topic (you will create a sample).

---

## Output

`faiss_search(topic: str) -> list[str]` — returns up to 3 relevant text chunks for a given topic.

---

## Files to Create/Modify

- `data/syllabus.txt` — sample syllabus text (create)
- `scripts/build_index.py` — one-time script to build the FAISS index (create)
- `main.py` — add FAISS load at startup + `faiss_search()` function (modify)

---

## Step 1: Create Sample Syllabus

Create `data/syllabus.txt`:

```
Ratio and Proportion: A ratio compares two quantities by division. If A:B = 2:3, then for every 2 units of A there are 3 units of B. Proportion states that two ratios are equal: A:B = C:D. Cross multiplication: A×D = B×C. Used in scaling recipes, maps, and financial calculations.

Percentage: Percentage means per hundred. To convert a fraction to percentage, multiply by 100. Example: 3/4 = 75%. Percentage increase = (new - old)/old × 100. Percentage decrease works the same way. Used in discounts, tax, interest calculations.

Simple Interest: Simple Interest = Principal × Rate × Time / 100. P is the initial amount, R is rate per year, T is time in years. Total amount = P + SI. Used in basic bank loans and savings accounts.

Compound Interest: In compound interest, interest is added to the principal each period. Formula: A = P(1 + R/100)^T. More powerful than simple interest over time. Used in most modern bank accounts and investments.

Average: Average = Sum of values / Number of values. Used to find the central tendency of a dataset. Weighted average accounts for different importance of each value. Average speed = total distance / total time.

Time and Work: If A can do a job in N days, A's one-day work = 1/N. Combined work rate = sum of individual rates. Time to complete together = 1 / (combined rate). Used in scheduling and resource planning.

Profit and Loss: Profit = Selling Price - Cost Price. Loss = Cost Price - Selling Price. Profit% = (Profit/CP) × 100. Discount is on Marked Price. Used in trade, business, and commerce.

Number System: Natural numbers, whole numbers, integers, rational, irrational, real numbers. Divisibility rules: divisible by 2 if even, by 3 if digit sum divisible by 3, by 9 similarly. LCM and HCF: LCM × HCF = product of two numbers.
```

---

## Step 2: Build Index Script

Create `scripts/build_index.py`:

```python
"""
Run once to build the FAISS index from data/syllabus.txt.
Usage: python scripts/build_index.py
"""
import faiss
import numpy as np
import json
import os

# Simple character-level bag-of-words embedding (no external model needed)
def text_to_vector(text: str, dim: int = 128) -> np.ndarray:
    """
    Deterministic hash-based embedding. Good enough for demo retrieval.
    For production: replace with sentence-transformers.
    """
    vec = np.zeros(dim, dtype=np.float32)
    for i, char in enumerate(text.lower()):
        vec[ord(char) % dim] += 1.0
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec

def build_index():
    with open("data/syllabus.txt") as f:
        raw = f.read()
    
    # Split on double newline → one chunk per paragraph
    chunks = [c.strip() for c in raw.split("\n\n") if c.strip()]
    
    dim = 128
    index = faiss.IndexFlatIP(dim)  # Inner product (cosine if normalized)
    
    vectors = []
    for chunk in chunks:
        vec = text_to_vector(chunk, dim)
        vectors.append(vec)
    
    matrix = np.stack(vectors)
    index.add(matrix)
    
    os.makedirs("data", exist_ok=True)
    faiss.write_index(index, "data/index.faiss")
    
    with open("data/chunks.json", "w") as f:
        json.dump(chunks, f, indent=2)
    
    print(f"Built index with {len(chunks)} chunks → data/index.faiss")

if __name__ == "__main__":
    build_index()
```

Run it:
```bash
python scripts/build_index.py
```

---

## Step 3: Add to main.py

Add at the top of `main.py` (after imports):

```python
import faiss
import numpy as np
import json

# ── FAISS Setup ──────────────────────────────────────────────────────────────

FAISS_INDEX = None
FAISS_CHUNKS = []

def text_to_vector(text: str, dim: int = 128) -> np.ndarray:
    """Must match the same function used in build_index.py exactly."""
    vec = np.zeros(dim, dtype=np.float32)
    for i, char in enumerate(text.lower()):
        vec[ord(char) % dim] += 1.0
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec = vec / norm
    return vec

@app.on_event("startup")
def load_faiss():
    global FAISS_INDEX, FAISS_CHUNKS
    if os.path.exists("data/index.faiss") and os.path.exists("data/chunks.json"):
        FAISS_INDEX = faiss.read_index("data/index.faiss")
        with open("data/chunks.json") as f:
            FAISS_CHUNKS = json.load(f)
        print(f"FAISS loaded: {len(FAISS_CHUNKS)} chunks")
    else:
        print("WARNING: FAISS index not found. Run scripts/build_index.py first.")

def faiss_search(topic: str, top_k: int = 3) -> list:
    """Return up to top_k relevant text chunks for the topic."""
    if FAISS_INDEX is None or len(FAISS_CHUNKS) == 0:
        return []
    
    query_vec = text_to_vector(topic).reshape(1, -1)
    distances, indices = FAISS_INDEX.search(query_vec, top_k)
    
    results = []
    for dist, idx in zip(distances[0], indices[0]):
        if idx >= 0 and dist > 0.1:   # min similarity threshold
            results.append(FAISS_CHUNKS[idx])
    
    return results
```

---

## curl Test

Add a temporary debug route:

```python
@app.get("/debug/faiss/{topic}")
def debug_faiss(topic: str):
    chunks = faiss_search(topic)
    return {"topic": topic, "chunks_found": len(chunks), "chunks": chunks}
```

```bash
curl "http://localhost:8000/debug/faiss/Ratio%20and%20Proportion"
```

**Expected:**
```json
{
  "topic": "Ratio and Proportion",
  "chunks_found": 3,
  "chunks": ["Ratio and Proportion: A ratio compares...", "..."]
}
```

---

## Done When

- `python scripts/build_index.py` runs without error
- `data/index.faiss` and `data/chunks.json` exist
- App starts and prints `FAISS loaded: 8 chunks`
- `/debug/faiss/Ratio` returns at least 1 chunk
