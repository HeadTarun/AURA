"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";

type LoginResponse = {
  token: string;
  student_id: string;
  name: string;
};

const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [rememberMe, setRememberMe] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");

    const trimmedEmail = email.trim();

    if (!trimmedEmail || !password) {
      setError("All fields are required.");
      return;
    }

    if (!emailPattern.test(trimmedEmail)) {
      setError("Please enter a valid email address.");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    setLoading(true);

    try {
      const response = await fetch("/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: trimmedEmail,
          password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data?.error || "Invalid credentials.");
      }

      const session = data as LoginResponse;
      const storage = rememberMe ? window.localStorage : window.sessionStorage;

      storage.setItem("aiTutorToken", session.token);
      storage.setItem(
        "aiTutorStudent",
        JSON.stringify({
          studentId: session.student_id,
          name: session.name,
        }),
      );

      window.location.href = "/dashboard";
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
        <Link className="signup-link" href="/signup">
          Sign up
        </Link>
      </header>

      <div className="star-field" aria-hidden="true">
        {Array.from({ length: 28 }, (_, index) => (
          <span key={index} className={`star star-${index + 1}`} />
        ))}
      </div>

      <section className="login-stage" aria-labelledby="login-heading">
        <div className="assistant-row" aria-hidden="true">
          <div className="pixel-computer">
            <span className="monitor" />
            <span className="face" />
            <span className="base" />
          </div>
          <div className="speech-bubble">Log in to continue your progress :)</div>
        </div>

        <form className="login-card" onSubmit={handleSubmit} noValidate>
          <div className="provider-grid" aria-label="Social login options">
            <button className="provider-button" type="button">
              <span className="google-mark" aria-hidden="true">
                G
              </span>
              Google
            </button>
            <button className="provider-button" type="button">
              <span className="github-mark" aria-hidden="true">
                GH
              </span>
              GitHub
            </button>
          </div>

          <div className="divider">
            <span>OR</span>
          </div>

          <h1 id="login-heading">Welcome Back</h1>

          <label className="field-label" htmlFor="email">
            Email / Username
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
            autoComplete="current-password"
            placeholder="Password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />

          <div className="form-row">
            <label className="remember-option">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={(event) => setRememberMe(event.target.checked)}
              />
              <span>Remember me</span>
            </label>
            <Link href="/forgot-password">Forgot password?</Link>
          </div>

          {error ? (
            <p className="error-message" role="alert">
              {error}
            </p>
          ) : null}

          <button className="login-button" type="submit" disabled={loading}>
            {loading ? "Logging in..." : "Login"}
          </button>

          <p className="terms-copy">
            By logging in, I agree to AI Tutor&apos;s <Link href="/terms">Terms</Link>.
          </p>

          <p className="account-copy">
            New here? <Link href="/signup">Create account</Link>
          </p>
        </form>
      </section>

      <div className="moon-band moon-left" aria-hidden="true" />
      <div className="moon-band moon-right" aria-hidden="true" />
    </main>
  );
}
