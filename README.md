# Adaptive AI Tutor - AURA

AURA started as a simple question: *What if learning felt like a guided conversation instead of a static page?*  
This repository is my attempt to answer that with a system that **teaches**, **tests**, and **adapts** in one flow.

The core idea is an AI tutor that remembers a learner's session, generates a lesson, asks a quiz, evaluates the answer, and nudges the difficulty up or down. It's built as a working API-first backend so it can plug into any future UI without rewriting the brain.

## Goal

Build a demo‑ready adaptive learning engine that turns a student's topic into:
1. a grounded lesson,  
2. a targeted quiz,  
3. an evaluation + gamified feedback,  
4. and optional career guidance.

## System Architecture (Big Picture)

```
Client (Web/Mobile)
        │
        ▼
FastAPI Backend
  ├─ POST /learn      → RAG retrieval + lesson generation
  ├─ POST /quiz       → quiz generation
  ├─ POST /evaluate   → evaluation + gamification + adaptation
  └─ POST /career     → career guidance
        │
        ├─ LLM Client (Gemini → Groq fallback, strict JSON)
        ├─ RAG Pipeline (LangChain + Chroma + BM25)
        └─ Session Store (JSON files per student)
```

## Working Project: What Runs Today

- **FastAPI backend** with `/learn`, `/quiz`, `/evaluate`, and `/career` routes.
- **Session persistence** via JSON files (`sessions/{student_id}.json`) with guardrails and repair.
- **LLM orchestration** using Gemini first, Groq as fallback, returning strict JSON payloads.
- **RAG retrieval** from `app/rag` using a hybrid vector + BM25 retriever to ground lessons.
- **Deterministic adaptation** logic that upgrades/downgrades level based on recent answers.

## Run Locally (Backend)

```bash
docker compose watch
```

Backend-only run without Docker:

```bash
cd backend
fastapi dev app/main.py
```

## Demo Video
https://drive.google.com/file/d/11WCGo62uSYTrHUNIDJSknhED0SaR7OUO/view?usp=drive_link

---

## 🚀 Upcoming Features — AURA Agent v2

> *From a reactive tutor to a proactive learning companion.*

The next major evolution of AURA is a fully **agentic learning system** built around the student's own resources and real-world schedule. Here's what's coming:

---

### 📁 Upload Your Own Resources
Students upload their own study materials — PDFs, notes, slides, or textbooks. The agent parses and indexes them, so every lesson is grounded in *your* content, not generic internet knowledge.

---

### 🗓️ Agent-Planned Curriculum with Deadlines
Tell AURA your goal and your deadline (exam date, job interview, course end). The agent:
- Breaks the material into **day-by-day learning milestones**
- Auto-schedules concepts based on complexity and dependency
- Adjusts the plan dynamically if you fall behind or race ahead

```
Upload: "Operating Systems - Silberschatz.pdf"
Goal:   "OS exam in 21 days"

→ Agent generates a 21-day plan:
   Day 1  → Processes & Threads
   Day 2  → CPU Scheduling
   Day 3  → Memory Management
   ...
```

---

### 🧑‍🏫 Daily Agent Teaching — Sarcastic & Interactive
Every day the agent picks up exactly where you left off and **teaches** the scheduled concept in a conversational, slightly sarcastic style — because dry reading puts you to sleep.

- Concepts explained with analogies, jokes, and real-world examples
- Socratic questioning: the agent asks *you* before explaining
- Mid-lesson check-ins to catch confusion early
- Tone adapts to your preference (chill / serious / roast mode 🔥)

---

### 🧠 Deep Personalization
The more you use AURA, the better it knows you:
- Tracks which concept types you consistently struggle with
- Remembers your preferred explanation style
- Adjusts quiz difficulty, pacing, and tone per-student
- Builds a **personal knowledge graph** over time

---

### 📊 Goal & Progress Tracking Dashboard
A dedicated view to keep you honest:
- Daily streak and completion rate
- Concept mastery heatmap (green = solid, red = revisit)
- Deadline countdown with projected finish date
- "At risk" alerts when you're falling behind the plan

---

### 💼 Career-Aware Learning Paths
AURA connects what you're learning to where you want to go:
- Input a target role (e.g. *"ML Engineer at a startup"*)
- Agent surfaces the most career-relevant concepts first
- Suggests skills to add based on job market signals
- Maps your current progress to real job readiness

---

### Architecture Preview (Agent v2)

```
Student Upload (PDF / Notes)
        │
        ▼
  Resource Indexer (RAG)
        │
        ▼
  Planner Agent  ←──── Deadline + Goal Input
        │  generates curriculum
        ▼
  Daily Teacher Agent
  ├─ Lesson (sarcastic, interactive)
  ├─ Quiz + Evaluation
  ├─ Personalization Update
  └─ Progress Store
        │
        ▼
  Progress Dashboard  ──→  Career Guidance Agent
```

---

> Contributions and feedback welcome — open an issue or start a discussion!
