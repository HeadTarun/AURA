"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { getCareerGuidance, CareerResult } from "@/lib/api";

export default function CareerPage() {
  const [goal, setGoal] = useState("");
  const [level, setLevel] = useState<"beginner" | "intermediate" | "advanced">("beginner");
  const [completedTopics, setCompletedTopics] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<CareerResult | null>(null);
  const [error, setError] = useState("");

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!goal.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const topics = completedTopics
        .split(",")
        .map((t) => t.trim())
        .filter(Boolean);
      const data = await getCareerGuidance(goal.trim(), topics, level);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to fetch career guidance.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="quiz-screen">
      <header className="quiz-nav" aria-label="Career navigation">
        <Link className="brand" href="/" aria-label="AI Tutor home">
          <span className="brand-coin" aria-hidden="true" />
          <span>AI Tutor</span>
        </Link>
        <nav style={{ display: "flex", gap: "1.5rem" }}>
          <Link href="/learn">Learn</Link>
          <Link href="/quiz">Quiz</Link>
          <Link href="/career" style={{ fontWeight: 700 }}>Career</Link>
        </nav>
        <Link href="/signup" className="signup-link">Sign up</Link>
      </header>

      <div className="star-field" aria-hidden="true">
        {Array.from({ length: 28 }, (_, i) => (
          <span key={i} className={`star star-${i + 1}`} />
        ))}
      </div>

      <section className="quiz-stage" style={{ paddingTop: "2rem" }}>
        <div className="assistant-row quiz-assistant" aria-hidden="true">
          <div className="pixel-computer">
            <span className="monitor" />
            <span className="face" />
            <span className="base" />
          </div>
          <div className="speech-bubble">Tell me your goal and I'll map your path! 🚀</div>
        </div>

        <div className="quiz-card" style={{ maxWidth: 640 }}>
          <h1 style={{ marginBottom: "1.5rem" }}>Career Guidance</h1>

          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            <div>
              <label style={{ display: "block", marginBottom: "0.4rem", fontWeight: 600 }}>
                What's your career goal?
              </label>
              <input
                type="text"
                placeholder="e.g. Become a machine learning engineer"
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                style={{ width: "100%", padding: "0.6rem 1rem", borderRadius: 8, border: "1px solid #ccc", fontSize: "1rem", boxSizing: "border-box" }}
              />
            </div>

            <div>
              <label style={{ display: "block", marginBottom: "0.4rem", fontWeight: 600 }}>
                Your current level
              </label>
              <select
                value={level}
                onChange={(e) => setLevel(e.target.value as typeof level)}
                style={{ width: "100%", padding: "0.6rem 1rem", borderRadius: 8, border: "1px solid #ccc", fontSize: "1rem" }}
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>

            <div>
              <label style={{ display: "block", marginBottom: "0.4rem", fontWeight: 600 }}>
                Topics you've already completed (comma-separated, optional)
              </label>
              <input
                type="text"
                placeholder="e.g. Python, data types, functions"
                value={completedTopics}
                onChange={(e) => setCompletedTopics(e.target.value)}
                style={{ width: "100%", padding: "0.6rem 1rem", borderRadius: 8, border: "1px solid #ccc", fontSize: "1rem", boxSizing: "border-box" }}
              />
            </div>

            {error && <p role="alert" style={{ color: "#e74c3c" }}>{error}</p>}

            <button
              type="submit"
              disabled={loading || !goal.trim()}
              className="quiz-primary-button"
            >
              {loading ? "Generating roadmap…" : "Get My Career Roadmap"}
            </button>
          </form>

          {result && <CareerCard result={result} />}
        </div>
      </section>

      <div className="moon-band moon-left" aria-hidden="true" />
      <div className="moon-band moon-right" aria-hidden="true" />
    </main>
  );
}

function CareerCard({ result }: { result: CareerResult }) {
  return (
    <div
      style={{
        marginTop: "2rem",
        padding: "1.5rem",
        borderRadius: 12,
        background: "rgba(108,99,255,0.08)",
        border: "1px solid rgba(108,99,255,0.25)",
      }}
    >
      <h2 style={{ marginBottom: "1rem" }}>Your Roadmap</h2>

      {result.advice && (
        <p style={{ marginBottom: "1rem", lineHeight: 1.7 }}>{result.advice}</p>
      )}

      {result.timeline && (
        <p style={{ marginBottom: "1rem" }}>
          <strong>⏱ Timeline:</strong> {result.timeline}
        </p>
      )}

      {result.roles && result.roles.length > 0 && (
        <>
          <strong>🎯 Target Roles</strong>
          <ul style={{ paddingLeft: "1.2rem", marginTop: "0.4rem", lineHeight: 1.8 }}>
            {result.roles.map((r, i) => <li key={i}>{r}</li>)}
          </ul>
        </>
      )}

      {result.skills && result.skills.length > 0 && (
        <>
          <strong style={{ display: "block", marginTop: "1rem" }}>🛠 Skills to Learn</strong>
          <ul style={{ paddingLeft: "1.2rem", marginTop: "0.4rem", lineHeight: 1.8 }}>
            {result.skills.map((s, i) => <li key={i}>{s}</li>)}
          </ul>
        </>
      )}

      {result.roadmap && result.roadmap.length > 0 && (
        <>
          <strong style={{ display: "block", marginTop: "1rem" }}>🗺 Step-by-Step Plan</strong>
          <ol style={{ paddingLeft: "1.2rem", marginTop: "0.4rem", lineHeight: 1.8 }}>
            {result.roadmap.map((step, i) => <li key={i}>{step}</li>)}
          </ol>
        </>
      )}

      {/* Any other string fields the backend returns */}
      {Object.entries(result)
        .filter(([k]) => !["advice", "timeline", "roles", "skills", "roadmap"].includes(k))
        .map(([k, v]) =>
          typeof v === "string" ? (
            <p key={k} style={{ marginTop: "0.75rem" }}>
              <strong style={{ textTransform: "capitalize" }}>{k.replace(/_/g, " ")}:</strong> {v}
            </p>
          ) : null
        )}

      <div style={{ marginTop: "1.5rem", display: "flex", gap: "0.75rem" }}>
        <Link href="/learn" className="quiz-primary-button" style={{ textDecoration: "none", display: "inline-block", textAlign: "center" }}>
          Start Learning →
        </Link>
        <Link href="/quiz" className="quiz-secondary-button" style={{ textDecoration: "none", display: "inline-block", textAlign: "center", padding: "0.6rem 1.2rem", borderRadius: 8, border: "1px solid rgba(255,255,255,0.3)" }}>
          Take a Quiz
        </Link>
      </div>
    </div>
  );
}
