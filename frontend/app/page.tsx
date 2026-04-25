"use client";

import Link from "next/link";

const stars = [
  { w: 7, h: 7, l: "6%", t: "8%" },
  { w: 7, h: 7, l: "17%", t: "28%" },
  { w: 10, h: 10, l: "27%", t: "13%" },
  { w: 7, h: 7, l: "39%", t: "22%" },
  { w: 7, h: 7, l: "53%", t: "44%" },
  { w: 10, h: 10, l: "66%", t: "18%" },
  { w: 7, h: 7, l: "78%", t: "36%" },
  { w: 7, h: 7, l: "88%", t: "14%" },
  { w: 7, h: 7, l: "4%", t: "56%" },
  { w: 7, h: 7, l: "23%", t: "64%" },
  { w: 10, h: 10, l: "48%", t: "70%" },
  { w: 7, h: 7, l: "82%", t: "60%" },
];

const ctaBandStars = [
  { w: 7, h: 7, l: "8%", t: "20%" },
  { w: 10, h: 10, l: "32%", t: "15%" },
  { w: 7, h: 7, l: "58%", t: "30%" },
  { w: 7, h: 7, l: "78%", t: "18%" },
  { w: 7, h: 7, l: "92%", t: "40%" },
];

const tickerItems = [
  "Python", "Data Science", "React", "Machine Learning",
  "Web Dev", "AI & ML", "Algorithms", "SQL", "TypeScript", "DevOps",
  "Python", "Data Science", "React", "Machine Learning",
  "Web Dev", "AI & ML", "Algorithms", "SQL", "TypeScript", "DevOps",
];

const tracks = [
  { cls: "lp-trk-python", label: "Python Path", title: "The Legend of Python", xp: "1,240 XP" },
  { cls: "lp-trk-data", label: "Data Science", title: "Data Crystal Quest", xp: "860 XP" },
  { cls: "lp-trk-web", label: "Web Dev", title: "Frontend Skyport", xp: "1,710 XP" },
  { cls: "lp-trk-ai", label: "AI & ML", title: "Machine Mind Citadel", xp: "430 XP" },
];

export default function LandingPage() {
  return (
    <main className="lp-root">
      {/* NAV */}
      <nav className="lp-topnav">
        <Link className="brand" href="/" aria-label="AI Tutor home">
          <span className="brand-coin" aria-hidden="true" />
          <span>AI Tutor</span>
        </Link>
        <div className="lp-nav-links">
          <a href="#lp-features">Features</a>
          <a href="#lp-about">About</a>
          <Link href="/login">Login</Link>
        </div>
        <Link className="lp-btn-signup" href="/signup">Sign up</Link>
      </nav>

      {/* HERO */}
      <section className="lp-hero">
        <div className="lp-stars" aria-hidden="true">
          {stars.map((s, i) => (
            <span key={i} className="lp-star" style={{ width: s.w, height: s.h, left: s.l, top: s.t }} />
          ))}
        </div>

        {/* World art */}
        <div className="lp-world-art" aria-hidden="true">
          <div className="lp-sky-grid" />
          <div className="lp-w-sun" />
          <div className="lp-w-ring" />
          <div className="lp-w-cloud lp-cloud-a" />
          <div className="lp-w-cloud lp-cloud-b" />
          <div className="lp-w-island">
            <span className="lp-w-tower" />
            <span className="lp-w-tree lp-w-tree-a" />
            <span className="lp-w-tree lp-w-tree-b" />
          </div>
          <div className="lp-w-float">
            <span className="lp-w-gem" />
            <span className="lp-w-fbase" />
          </div>
        </div>

        <div className="lp-hero-copy">
          <div className="lp-eyebrow">Level up your skills</div>
          <h1 className="lp-hero-h1">Your AI Learning<br />Companion</h1>
          <p className="lp-hero-sub">
            Personalised lessons, instant quizzes, and real career guidance — all powered by AI and built for serious learners.
          </p>
          <div className="lp-cta-row">
            <Link className="lp-btn-cta-p" href="/signup">Get Started →</Link>
            <Link className="lp-btn-cta-s" href="/login">Login</Link>
          </div>

          <div className="lp-mascot-row" aria-hidden="true">
            <div className="pixel-computer lp-pixel-pc">
              <span className="monitor" />
              <span className="face" />
              <span className="base" />
            </div>
            <div className="lp-bubble">Ready to start your quest? 🎮</div>
          </div>
        </div>
      </section>

      {/* TICKER */}
      <div className="lp-ticker-wrap" aria-hidden="true">
        <div className="lp-ticker-inner">
          {tickerItems.map((item, i) => (
            <span key={i} className="lp-t-item">
              <span className="lp-t-dot" />
              {item}
            </span>
          ))}
        </div>
      </div>

      {/* FEATURES */}
      <section className="lp-section" id="lp-features">
        <div className="lp-kicker">Why AI Tutor?</div>
        <h2 className="lp-sec-h">Everything you need to learn faster</h2>
        <div className="lp-feat-grid">
          <div className="lp-feat-card lp-feat-blue">
            <div className="lp-feat-icon">🧠</div>
            <h3>AI Learning</h3>
            <p>Type any topic and get a personalised lesson instantly — tailored to your exact level and pacing.</p>
          </div>
          <div className="lp-feat-card lp-feat-yellow">
            <div className="lp-feat-icon">🎯</div>
            <h3>Progress Tracking</h3>
            <p>XP points, streaks, and badges keep you motivated and show exactly how far you&apos;ve come.</p>
          </div>
          <div className="lp-feat-card lp-feat-red">
            <div className="lp-feat-icon">📊</div>
            <h3>Weak Areas</h3>
            <p>After every quiz, the AI identifies gaps and auto-adjusts future lessons to close them.</p>
          </div>
          <div className="lp-feat-card lp-feat-teal">
            <div className="lp-feat-icon">🏆</div>
            <h3>Gamification</h3>
            <p>Earn XP, unlock badges, and level up as you master topics — learning feels like an RPG quest.</p>
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="lp-section lp-how-section" id="lp-about">
        <div className="lp-kicker">How it works</div>
        <h2 className="lp-sec-h">Three steps to mastery</h2>
        <div className="lp-steps-row">
          <div className="lp-step-card">
            <div className="lp-step-num">01</div>
            <h3>Learn</h3>
            <p>Enter any topic. The AI generates a custom lesson with key points and examples.</p>
          </div>
          <div className="lp-step-arrow" aria-hidden="true">→</div>
          <div className="lp-step-card">
            <div className="lp-step-num">02</div>
            <h3>Quiz</h3>
            <p>Test yourself with AI-generated questions based on exactly what you just learned.</p>
          </div>
          <div className="lp-step-arrow" aria-hidden="true">→</div>
          <div className="lp-step-card">
            <div className="lp-step-num">03</div>
            <h3>Evaluate</h3>
            <p>Get instant feedback, your score, weak areas, and a personalised improvement tip.</p>
          </div>
        </div>
      </section>

      {/* TRACKS PREVIEW */}
      <section className="lp-section">
        <div className="lp-kicker">Learning Tracks</div>
        <h2 className="lp-sec-h">Choose your quest</h2>
        <div className="lp-prev-grid">
          {tracks.map((trk) => (
            <Link key={trk.cls} className={`lp-prev-track ${trk.cls}`} href="/learn">
              <span className="lp-trk-art">
                <span className="lp-art-sky" />
                <span className="lp-art-land" />
                <span className="lp-art-marker" />
              </span>
              <span className="lp-prev-label">{trk.label}</span>
              <span className="lp-prev-title">{trk.title}</span>
              <span className="lp-prev-xp">{trk.xp}</span>
            </Link>
          ))}
        </div>
        <div className="lp-center-cta">
          <Link className="lp-btn-cta-p" href="/learn">Browse all tracks →</Link>
        </div>
      </section>

      {/* CTA BAND */}
      <section className="lp-cta-band">
        <div className="lp-stars" aria-hidden="true">
          {ctaBandStars.map((s, i) => (
            <span key={i} className="lp-star" style={{ width: s.w, height: s.h, left: s.l, top: s.t }} />
          ))}
        </div>
        <div className="lp-cta-inner">
          <div className="pixel-computer lp-pixel-pc lp-cta-pc" aria-hidden="true">
            <span className="monitor" />
            <span className="face" />
            <span className="base" />
          </div>
          <div>
            <h2>Start learning today</h2>
            <p>Join thousands of learners already levelling up with AI Tutor.</p>
            <div className="lp-cta-row">
              <Link className="lp-btn-cta-p" href="/signup">Create free account →</Link>
              <Link className="lp-btn-cta-s" href="/login">I already have an account</Link>
            </div>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="lp-footer">
        <div className="lp-foot-brand">
          <Link className="brand" href="/" aria-label="AI Tutor home">
            <span className="brand-coin" aria-hidden="true" />
            <span>AI Tutor</span>
          </Link>
          <p>Your AI learning companion.</p>
        </div>
        <div className="lp-foot-links">
          <Link href="/learn">Learn</Link>
          <Link href="/quiz">Quiz</Link>
          <Link href="/career">Career</Link>
          <Link href="/login">Login</Link>
          <Link href="/signup">Sign up</Link>
        </div>
        <div className="lp-foot-copy">© 2025 AI Tutor. All rights reserved.</div>
      </footer>

      <div className="moon-band moon-left" aria-hidden="true" />
      <div className="moon-band moon-right" aria-hidden="true" />
    </main>
  );
}
