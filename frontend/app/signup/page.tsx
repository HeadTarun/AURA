"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { signup } from "@/lib/api";

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function SignupPage() {
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    const trimmedName = name.trim();
    const trimmedEmail = email.trim();

    if (!trimmedName || !trimmedEmail || !password || !confirmPassword) {
      setError("All fields are required.");
      return;
    }

    if (!emailPattern.test(trimmedEmail)) {
      setError("Please enter a valid email address.");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters.");
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      await signup(trimmedEmail, password, trimmedName);
      window.location.href = "/login";
    } catch (requestError) {
      setError(
        requestError instanceof Error
          ? requestError.message
          : "Something went wrong. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="login-screen">
      <header className="site-nav" aria-label="Main navigation">
        <Link className="brand" href="/" aria-label="AI Tutor home">
          <span className="brand-coin" aria-hidden="true" />
          <span>AI Tutor</span>
        </Link>
        <nav className="nav-links" aria-label="Primary">
          <a href="#learn">Learn</a>
          <a href="#practice">Practice</a>
          <a href="#build">Build</a>
          <a href="#community">Community</a>
        </nav>
        <Link className="signup-link" href="/login">
          Log in
        </Link>
      </header>

      <div className="star-field" aria-hidden="true">
        {Array.from({ length: 28 }, (_, index) => (
          <span key={index} className={`star star-${index + 1}`} />
        ))}
      </div>

      <section className="login-stage signup-stage" aria-labelledby="signup-heading">
        <div className="assistant-row" aria-hidden="true">
          <div className="pixel-computer">
            <span className="monitor" />
            <span className="face" />
            <span className="base" />
          </div>
          <div className="speech-bubble">
            Create an account to save your progress :)
          </div>
        </div>

        <form className="login-card signup-card" onSubmit={handleSubmit} noValidate>
          <h1 id="signup-heading">Create Account</h1>

          <label className="field-label" htmlFor="name">
            Full Name
          </label>
          <input
            id="name"
            name="name"
            type="text"
            autoComplete="name"
            placeholder="John Doe"
            value={name}
            onChange={(event) => setName(event.target.value)}
          />

          <label className="field-label" htmlFor="email">
            Email
          </label>
          <input
            id="email"
            name="email"
            type="email"
            autoComplete="email"
            placeholder="student@example.com"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
          />

          <label className="field-label" htmlFor="password">
            Password
          </label>
          <input
            id="password"
            name="password"
            type="password"
            autoComplete="new-password"
            placeholder="Min 8 characters"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />

          <label className="field-label" htmlFor="confirm-password">
            Confirm Password
          </label>
          <input
            id="confirm-password"
            name="confirm-password"
            type="password"
            autoComplete="new-password"
            placeholder="Confirm password"
            value={confirmPassword}
            onChange={(event) => setConfirmPassword(event.target.value)}
          />

          {error ? (
            <p className="error-message" role="alert">
              {error}
            </p>
          ) : null}

          <button className="login-button" type="submit" disabled={loading}>
            {loading ? "Creating account…" : "Sign up for free"}
          </button>

          <p className="account-copy">
            Already have an account? <Link href="/login">Log in</Link>
          </p>
        </form>
      </section>

      <div className="moon-band moon-left" aria-hidden="true" />
      <div className="moon-band moon-right" aria-hidden="true" />
    </main>
  );
}
