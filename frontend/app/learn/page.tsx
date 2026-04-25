"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

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
  },
];

export default function LearnPage() {
  const [tracks, setTracks] = useState<Track[]>(fallbackTracks);
  const [selectedTrack, setSelectedTrack] = useState<Track>(fallbackTracks[0]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let active = true;

    async function loadTracks() {
      try {
        const response = await fetch("/learn");

        if (!response.ok) {
          throw new Error("Using local learning tracks");
        }

        const data = (await response.json()) as Partial<Track>[];
        const hydratedTracks = data.map((track, index) => ({
          ...fallbackTracks[index % fallbackTracks.length],
          ...track,
        })) as Track[];

        if (active && hydratedTracks.length > 0) {
          setTracks(hydratedTracks);
          setSelectedTrack(hydratedTracks[0]);
        }
      } catch {
        if (active) {
          setTracks(fallbackTracks);
          setSelectedTrack(fallbackTracks[0]);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadTracks();

    return () => {
      active = false;
    };
  }, []);

  return (
    <main className="learn-page">
      <Navbar />
      <Hero />

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
          <div className="track-grid" aria-busy={loading}>
            {tracks.map((track) => (
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
            <Link className="roadmap-button" href={`/learn/${selectedTrack.id}`}>
              Open roadmap
            </Link>
          </aside>
        </div>
      </section>
    </main>
  );
}

function Navbar() {
  return (
    <header className="learn-nav" aria-label="Main navigation">
      <Link className="brand" href="/" aria-label="AI Tutor home">
        <span className="brand-coin" aria-hidden="true" />
        <span>AI Tutor</span>
      </Link>
      <nav className="learn-links" aria-label="Primary">
        <Link className="active" href="/learn">
          Learn
        </Link>
        <a href="#practice">Practice</a>
        <a href="#build">Build</a>
        <a href="#community">Community</a>
        <a href="#pricing">Pricing</a>
      </nav>
      <div className="nav-actions">
        <button className="icon-button" type="button" aria-label="Search">
          <span className="search-icon" aria-hidden="true" />
        </button>
        <button className="icon-button" type="button" aria-label="Toggle theme">
          <span className="moon-icon" aria-hidden="true" />
        </button>
        <Link className="signup-link" href="/signup">
          Sign up
        </Link>
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
        <p>
          Start your coding journey with interactive lessons and real-world
          projects.
        </p>
        <Link className="hero-cta" href="#tracks-heading">
          Start Learning
        </Link>
      </div>
    </section>
  );
}

function TrackCard({
  track,
  selected,
  onSelect,
}: Readonly<{
  track: Track;
  selected: boolean;
  onSelect: () => void;
}>) {
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
        <span className={`difficulty ${track.difficulty.toLowerCase()}`}>
          {track.difficulty}
        </span>
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
