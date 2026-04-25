// lib/api.ts — Central API client
// All calls go through /api/v1/* on the backend (http://localhost:8000)

const BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? "";
const API = `${BASE_URL}/api/v1`;

// ─── Token helpers ────────────────────────────────────────────────────────────

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return (
    window.localStorage.getItem("aiTutorToken") ??
    window.sessionStorage.getItem("aiTutorToken") ??
    null
  );
}

export function getStudentId(): string {
  if (typeof window === "undefined") return "guest";
  try {
    const raw =
      window.localStorage.getItem("aiTutorStudent") ??
      window.sessionStorage.getItem("aiTutorStudent");
    if (raw) {
      const parsed = JSON.parse(raw) as { studentId?: string };
      if (parsed.studentId) return parsed.studentId;
    }
  } catch {
    // ignore
  }
  // Fall back to a stable guest ID stored in localStorage
  let guestId = window.localStorage.getItem("aiTutorGuestId");
  if (!guestId) {
    guestId = `guest_${Math.random().toString(36).slice(2, 10)}`;
    window.localStorage.setItem("aiTutorGuestId", guestId);
  }
  return guestId;
}

export function clearSession(): void {
  ["aiTutorToken", "aiTutorStudent"].forEach((k) => {
    window.localStorage.removeItem(k);
    window.sessionStorage.removeItem(k);
  });
}

// ─── Base fetch wrapper ───────────────────────────────────────────────────────

async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  requireAuth = false
): Promise<T> {
  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(options.headers as Record<string, string>),
  };

  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  else if (requireAuth) throw new Error("Not authenticated. Please log in.");

  const res = await fetch(`${API}${path}`, { ...options, headers });

  if (!res.ok) {
    let message = `Request failed (${res.status})`;
    try {
      const err = (await res.json()) as { detail?: string; message?: string };
      message = err.detail ?? err.message ?? message;
    } catch {
      // ignore parse errors
    }
    throw new Error(message);
  }

  return res.json() as Promise<T>;
}

// ─── Auth ─────────────────────────────────────────────────────────────────────

export interface LoginResult {
  access_token: string;
  token_type: string;
}

export interface UserPublic {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string | null;
}

/**
 * Login uses OAuth2 form encoding (username/password), NOT JSON.
 */
export async function login(
  email: string,
  password: string,
  remember: boolean
): Promise<UserPublic> {
  const body = new URLSearchParams({ username: email, password });

  const res = await fetch(`${API}/login/access-token`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: body.toString(),
  });

  if (!res.ok) {
    let message = "Invalid credentials.";
    try {
      const err = (await res.json()) as { detail?: string };
      if (err.detail) message = err.detail;
    } catch {
      // ignore
    }
    throw new Error(message);
  }

  const { access_token } = (await res.json()) as LoginResult;
  const storage = remember ? window.localStorage : window.sessionStorage;
  storage.setItem("aiTutorToken", access_token);

  // Fetch the user profile right after login
  const user = await getMe();
  storage.setItem(
    "aiTutorStudent",
    JSON.stringify({ studentId: user.id, name: user.full_name ?? user.email })
  );
  return user;
}

export async function signup(
  email: string,
  password: string,
  fullName: string
): Promise<UserPublic> {
  return apiFetch<UserPublic>("/users/signup", {
    method: "POST",
    body: JSON.stringify({ email, password, full_name: fullName }),
  });
}

export async function getMe(): Promise<UserPublic> {
  return apiFetch<UserPublic>("/users/me", {}, true);
}

// ─── Learn ────────────────────────────────────────────────────────────────────

export interface LearnResult {
  title?: string;
  summary?: string;
  content?: string;
  key_points?: string[];
  examples?: string[];
  [key: string]: unknown;
}

export async function learn(
  topic: string,
  level = "beginner"
): Promise<LearnResult> {
  const student_id = getStudentId();
  return apiFetch<LearnResult>("/learn", {
    method: "POST",
    body: JSON.stringify({ student_id, topic, level }),
  });
}

// ─── Quiz ─────────────────────────────────────────────────────────────────────

export interface QuizResult {
  question: string;
  options?: string[];
  answer: string;
  explanation?: string;
  [key: string]: unknown;
}

export async function generateQuiz(): Promise<QuizResult> {
  const student_id = getStudentId();
  return apiFetch<QuizResult>("/quiz", {
    method: "POST",
    body: JSON.stringify({ student_id }),
  });
}

// ─── Evaluate ─────────────────────────────────────────────────────────────────

export interface EvaluateResult {
  evaluation: {
    correct: boolean;
    feedback: string;
    explanation: string;
    next_level: string;
    improvement_tip: string;
    weak_areas: string[];
    score: number;
    confidence: number;
  };
  gamification: {
    xp_earned?: number;
    streak?: number;
    badge?: string | null;
    level_up?: boolean;
    [key: string]: unknown;
  };
}

export async function evaluate(studentAnswer: string): Promise<EvaluateResult> {
  const student_id = getStudentId();
  return apiFetch<EvaluateResult>("/evaluate", {
    method: "POST",
    body: JSON.stringify({ student_id, student_answer: studentAnswer }),
  });
}

// ─── Career ───────────────────────────────────────────────────────────────────

export interface CareerResult {
  roadmap?: string[];
  roles?: string[];
  skills?: string[];
  timeline?: string;
  advice?: string;
  [key: string]: unknown;
}

export async function getCareerGuidance(
  goal: string,
  completedTopics: string[] = [],
  level = "beginner"
): Promise<CareerResult> {
  return apiFetch<CareerResult>("/career", {
    method: "POST",
    body: JSON.stringify({
      goal,
      completed_topics: completedTopics,
      level,
    }),
  });
}
