"use client";

import Link from "next/link";
import { useState } from "react";
import { learn, LearnResult } from "@/lib/api";

type Track = {
  id: number;
  title: string;
  subtitle: string;
  description: string;
  progress: number;
  difficulty: "Beginner" | "Intermediate" | "Advanced";
  xp: number;
  badge: string;
  palette: "python" | "data" | "web" | "ai";
  lessons: string[];
  topic: string;
};

const fallbackTracks: Track[] = [
  {
    id: 1,
    title: "The Legend of Python",
    subtitle: "Python Path",
    description: "Beginner-friendly programming with real-world logic.",
    progress: 40,
    difficulty: "Beginner",
    xp: 1240,
    badge: "Starter",
    palette: "python",
    lessons: ["Variables", "Loops", "Functions", "Mini chatbot"],
    topic: "Python basics",
  },
  {
    id: 2,
    title: "Data Crystal Quest",
    subtitle: "Data Science Path",
    description: "Analyze data, build charts, and uncover useful patterns.",
    progress: 24,
    difficulty: "Intermediate",
    xp: 860,
    badge: "Explorer",
    palette: "data",
    lessons: ["Tables", "Cleaning", "Charts", "Insights"],
    topic: "Data science with Python",
  },
  {
    id: 3,
    title: "Frontend Skyport",
    subtitle: "Web Development Path",
    description: "Build responsive interfaces with HTML, CSS, and React.",
    progress: 58,
    difficulty: "Beginner",
    xp: 1710,
    badge: "Builder",
    palette: "web",
    lessons: ["Markup", "Layouts", "Components", "Deploy"],
    topic: "React and web development",
  },
  {
    id: 4,
    title: "Machine Mind Citadel",
    subtitle: "AI & ML Path",
    description: "Train models, evaluate predictions, and ship AI features.",
    progress: 12,
    difficulty: "Advanced",
    xp: 430,
    badge: "Scout",
    palette: "ai",
    lessons: ["Datasets", "Training", "Evaluation", "AI project"],
    topic: "Machine learning fundamentals",
  },
];

export default function LearnPage() {
  const [selectedTrack, setSelectedTrack] = useState<Track>(fallbackTracks[0]);
  const [customTopic, setCustomTopic] = useState("");
  const [level, setLevel] = useState<"beginner" | "intermediate" | "advanced">("beginner");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<LearnResult | null>(null);
  const [error, setError] = useState("");

  async function handleLearn(topic: string) {
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const data = await learn(topic, level);
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load lesson.");
    } finally {
      setLoading(false);
    }
  }

  function handleTrackLearn() {
    handleLearn(selectedTrack.topic);
  }

  function handleCustomLearn(e: React.FormEvent) {
    e.preventDefault();
    if (customTopic.trim()) handleLearn(customTopic.trim());
  }

  return (
    <main className="learn-page">
      <Navbar />
      <Hero />

      {/* ── Custom topic input ── */}
      <section style={{ padding: "2rem", maxWidth: 720, margin: "0 auto" }}>
        <h2 style={{ marginBottom: "1rem" }}>Ask the AI Tutor</h2>
        <form onSubmit={handleCustomLearn} style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap" }}>
          <input
            type="text"
            placeholder="Enter any topic (e.g. 'recursion', 'React hooks')"
            value={customTopic}
            onChange={(e) => setCustomTopic(e.target.value)}
            style={{ flex: 1, minWidth: 220, padding: "0.6rem 1rem", borderRadius: 8, border: "1px solid #ccc", fontSize: "1rem" }}
          />
          <select
            value={level}
            onChange={(e) => setLevel(e.target.value as typeof level)}
            style={{ padding: "0.6rem 1rem", borderRadius: 8, border: "1px solid #ccc", fontSize: "1rem" }}
          >
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
          <button
            type="submit"
            disabled={loading || !customTopic.trim()}
            style={{ padding: "0.6rem 1.4rem", borderRadius: 8, background: "#6c63ff", color: "#fff", border: "none", fontWeight: 700, cursor: "pointer", fontSize: "1rem" }}
          >
            {loading ? "Loading…" : "Learn Now"}
          </button>
        </form>

        {error && (
          <p role="alert" style={{ color: "#e74c3c", marginTop: "0.75rem" }}>{error}</p>
        )}

        {result && <LessonCard result={result} onQuiz={() => { window.location.href = "/quiz"; }} />}
      </section>

      {/* ── Learning Tracks ── */}
      <section className="track-section" aria-labelledby="tracks-heading">
        <div className="section-kicker">Learning Tracks</div>
        <div className="section-heading-row">
          <div>
            <h2 id="tracks-heading">Choose your next quest</h2>
            <p>
              Browse structured paths, keep your streak alive, and unlock lesson
              badges as you move from basics to real projects.
            </p>
          </div>
          <div className="player-stats" aria-label="Learning progress summary">
            <span>Level 7</span>
            <span>12 day streak</span>
            <span>4 badges</span>
          </div>
        </div>

        <div className="track-layout">
          <div className="track-grid">
            {fallbackTracks.map((track) => (
              <TrackCard
                key={track.id}
                track={track}
                selected={selectedTrack.id === track.id}
                onSelect={() => setSelectedTrack(track)}
              />
            ))}
          </div>

          <aside className="roadmap-panel" aria-label="Selected course roadmap">
            <div className="roadmap-orb" aria-hidden="true" />
            <p className="section-kicker">Active Roadmap</p>
            <h3>{selectedTrack.title}</h3>
            <p>{selectedTrack.description}</p>
            <ol>
              {selectedTrack.lessons.map((lesson, index) => (
                <li key={lesson}>
                  <span>{index + 1}</span>
                  {lesson}
                </li>
              ))}
            </ol>
            <button
              className="roadmap-button"
              type="button"
              onClick={handleTrackLearn}
              disabled={loading}
              style={{ cursor: "pointer" }}
            >
              {loading ? "Loading lesson…" : "Start this lesson →"}
            </button>
            <Link className="roadmap-button" href="/quiz" style={{ marginTop: "0.5rem", display: "block", textAlign: "center" }}>
              Take a Quiz
            </Link>
          </aside>
        </div>
      </section>
    </main>
  );
}

// ── Lesson result card ──────────────────────────────────────────────────────

function LessonCard({ result, onQuiz }: { result: LearnResult; onQuiz: () => void }) {
  return (
    <div
      style={{
        marginTop: "1.5rem",
        padding: "1.5rem",
        borderRadius: 12,
        background: "rgba(108,99,255,0.08)",
        border: "1px solid rgba(108,99,255,0.25)",
      }}
    >
      {result.title && <h3 style={{ marginBottom: "0.5rem" }}>{result.title}</h3>}
      {result.summary && <p style={{ marginBottom: "1rem", opacity: 0.85 }}>{result.summary}</p>}
      {result.content && (
        <p style={{ marginBottom: "1rem", whiteSpace: "pre-wrap", lineHeight: 1.7 }}>{result.content}</p>
      )}

      {result.key_points && result.key_points.length > 0 && (
        <>
          <strong>Key Points</strong>
          <ul style={{ marginTop: "0.4rem", paddingLeft: "1.2rem", lineHeight: 1.8 }}>
            {result.key_points.map((pt, i) => <li key={i}>{pt}</li>)}
          </ul>
        </>
      )}

      {result.examples && result.examples.length > 0 && (
        <>
          <strong style={{ marginTop: "1rem", display: "block" }}>Examples</strong>
          <ul style={{ marginTop: "0.4rem", paddingLeft: "1.2rem", lineHeight: 1.8 }}>
            {result.examples.map((ex, i) => <li key={i}>{ex}</li>)}
          </ul>
        </>
      )}

      {/* Render any other top-level string fields */}
      {Object.entries(result)
        .filter(([k]) => !["title", "summary", "content", "key_points", "examples"].includes(k))
        .map(([k, v]) =>
          typeof v === "string" ? (
            <p key={k} style={{ marginTop: "0.5rem" }}>
              <strong style={{ textTransform: "capitalize" }}>{k.replace(/_/g, " ")}:</strong> {v}
            </p>
          ) : null
        )}

      <button
        type="button"
        onClick={onQuiz}
        style={{
          marginTop: "1.25rem",
          padding: "0.6rem 1.4rem",
          borderRadius: 8,
          background: "#6c63ff",
          color: "#fff",
          border: "none",
          fontWeight: 700,
          cursor: "pointer",
          fontSize: "1rem",
        }}
      >
        Take the Quiz →
      </button>
    </div>
  );
}

// ── Sub-components (unchanged) ──────────────────────────────────────────────

function Navbar() {
  return (
    <header className="learn-nav" aria-label="Main navigation">
      <Link className="brand" href="/" aria-label="AI Tutor home">
        <span className="brand-coin" aria-hidden="true" />
        <span>AI Tutor</span>
      </Link>
      <nav className="learn-links" aria-label="Primary">
        <Link className="active" href="/learn">Learn</Link>
        <Link href="/quiz">Quiz</Link>
        <Link href="/career">Career</Link>
      </nav>
      <div className="nav-actions">
        <Link className="signup-link" href="/signup">Sign up</Link>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section className="learn-hero" aria-labelledby="learn-hero-title">
      <div className="world-art" aria-hidden="true">
        <div className="sky-grid" />
        <div className="sun" />
        <div className="planet-ring" />
        <div className="far-mountain far-one" />
        <div className="far-mountain far-two" />
        <div className="world-dome" />
        <div className="island island-left">
          <span className="tower" />
          <span className="tree tree-a" />
          <span className="tree tree-b" />
        </div>
        <div className="mountain-cluster">
          <span className="peak peak-one" />
          <span className="peak peak-two" />
          <span className="bridge" />
        </div>
        <div className="floating-campus">
          <span className="campus-gem" />
          <span className="campus-base" />
          <span className="campus-ray ray-one" />
          <span className="campus-ray ray-two" />
        </div>
        <div className="hero-cloud cloud-one" />
        <div className="hero-cloud cloud-two" />
      </div>

      <div className="hero-copy">
        <p>Explore the world of</p>
        <h1 id="learn-hero-title">AI Tutor</h1>
        <p>Start your coding journey with interactive lessons and real-world projects.</p>
        <a className="hero-cta" href="#tracks-heading">Start Learning</a>
      </div>
    </section>
  );
}

function TrackCard({
  track,
  selected,
  onSelect,
}: Readonly<{ track: Track; selected: boolean; onSelect: () => void }>) {
  return (
    <button
      className={`track-card ${selected ? "selected" : ""}`}
      type="button"
      onClick={onSelect}
      aria-pressed={selected}
    >
      <span className={`track-art ${track.palette}`} aria-hidden="true">
        <span className="art-sky" />
        <span className="art-land" />
        <span className="art-marker" />
      </span>
      <span className="track-meta">
        <span>{track.subtitle}</span>
        <span className={`difficulty ${track.difficulty.toLowerCase()}`}>{track.difficulty}</span>
      </span>
      <span className="track-title">{track.title}</span>
      <span className="track-description">{track.description}</span>
      <span className="progress-row">
        <span>{track.progress}% complete</span>
        <span>{track.xp} XP</span>
      </span>
      <span className="progress-track">
        <span style={{ width: `${track.progress}%` }} />
      </span>
      <span className="badge-chip">{track.badge} badge</span>
    </button>
  );
}
