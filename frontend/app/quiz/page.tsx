"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { generateQuiz, evaluate, QuizResult, EvaluateResult } from "@/lib/api";
import soundManager from "@/utils/soundManager";

const xpPerCorrect = 10;

export default function QuizPage() {
  const [quiz, setQuiz] = useState<QuizResult | null>(null);
  const [selectedOption, setSelectedOption] = useState("");
  const [evaluation, setEvaluation] = useState<EvaluateResult | null>(null);
  const [score, setScore] = useState(0);
  const [questionCount, setQuestionCount] = useState(0);
  const [totalCount, setTotalCount] = useState(0);
  const [loadingQuiz, setLoadingQuiz] = useState(true);
  const [loadingEval, setLoadingEval] = useState(false);
  const [finished, setFinished] = useState(false);
  const [error, setError] = useState("");

  const optionLetters = ["A", "B", "C", "D"];
  const options: string[] = useMemo(() => {
    if (!quiz) return [];
    if (Array.isArray(quiz.options) && quiz.options.length > 0) return quiz.options as string[];
    // If backend returns no options, build a minimal set with the correct answer
    return [quiz.answer, "I don't know"];
  }, [quiz]);

  async function loadNextQuiz() {
    setLoadingQuiz(true);
    setError("");
    setEvaluation(null);
    setSelectedOption("");
    try {
      const q = await generateQuiz();
      setQuiz(q);
      setQuestionCount((c) => c + 1);
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Could not load quiz. Make sure you have completed a /learn session first."
      );
    } finally {
      setLoadingQuiz(false);
    }
  }

  useEffect(() => {
    loadNextQuiz();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleAnswer(option: string) {
    if (evaluation || loadingEval) return;
    setSelectedOption(option);
    setLoadingEval(true);
    try {
      const result = await evaluate(option);
      setEvaluation(result);
      setTotalCount((c) => c + 1);
      if (result.evaluation.correct) {
        soundManager.play("success");
        setScore((s) => s + 1);
      } else {
        soundManager.play("error");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Evaluation failed.");
    } finally {
      setLoadingEval(false);
    }
  }

  async function handleNext() {
    soundManager.play("click");
    await loadNextQuiz();
  }

  function handleFinish() {
    soundManager.play("levelup");
    setFinished(true);
  }

  const xpEarned = score * xpPerCorrect;
  const badgeUnlocked = totalCount > 0 && score === totalCount;

  const resultTitle = useMemo(() => {
    if (badgeUnlocked) return "Perfect Clear";
    if (totalCount > 0 && score >= Math.ceil(totalCount * 0.7)) return "Level Passed";
    return "Keep Practicing";
  }, [badgeUnlocked, totalCount, score]);

  return (
    <main className="quiz-screen">
      <header className="quiz-nav" aria-label="Quiz navigation">
        <Link className="brand" href="/" aria-label="AI Tutor home">
          <span className="brand-coin" aria-hidden="true" />
          <span>AI Tutor</span>
        </Link>
        <Link className="quiz-back-link" href="/learn">Back to Learn</Link>
        <div className="quiz-nav-stats" aria-label="Quiz progress">
          <span>{xpEarned} XP</span>
          <span style={{ marginLeft: "1rem" }}>{score}/{totalCount} correct</span>
        </div>
      </header>

      <div className="star-field" aria-hidden="true">
        {Array.from({ length: 28 }, (_, index) => (
          <span key={index} className={`star star-${index + 1}`} />
        ))}
      </div>

      <section className="quiz-stage" aria-labelledby="quiz-title">
        <div className="assistant-row quiz-assistant" aria-hidden="true">
          <div className="pixel-computer">
            <span className="monitor" />
            <span className="face" />
            <span className="base" />
          </div>
          <div className="speech-bubble">
            {loadingQuiz ? "Loading your question…" : "Choose your answer and earn XP :)"}
          </div>
        </div>

        {finished ? (
          <ResultCard
            badgeUnlocked={badgeUnlocked}
            totalCount={totalCount}
            resultTitle={resultTitle}
            score={score}
            xpEarned={xpEarned}
            onRetry={() => {
              setScore(0);
              setTotalCount(0);
              setFinished(false);
              loadNextQuiz();
            }}
          />
        ) : error ? (
          <div className="quiz-card" style={{ textAlign: "center" }}>
            <p style={{ color: "#e74c3c", marginBottom: "1rem" }}>{error}</p>
            <p style={{ marginBottom: "1rem", opacity: 0.75 }}>
              You need to complete a <strong>Learn</strong> session first so the backend has a topic for the quiz.
            </p>
            <Link href="/learn" className="roadmap-button">
              Go to Learn →
            </Link>
          </div>
        ) : (
          <section className="quiz-card" aria-labelledby="quiz-title" aria-busy={loadingQuiz}>
            <div className="quiz-card-header">
              <p>Question {questionCount}</p>
              <span>{loadingQuiz ? "Loading…" : `${score}/${totalCount} correct`}</span>
            </div>

            <h1 id="quiz-title">Code Quest</h1>

            {loadingQuiz ? (
              <p style={{ textAlign: "center", padding: "2rem", opacity: 0.7 }}>Generating question…</p>
            ) : quiz ? (
              <>
                <div className="question-panel">
                  <p className="question-kicker">Question {questionCount}</p>
                  <h2>{quiz.question}</h2>
                </div>

                <div className="option-grid" role="list" aria-label="Answer options">
                  {options.map((option, index) => {
                    const isSelected = selectedOption === option;
                    const isAnswered = !!evaluation;
                    const isCorrect = isAnswered && option === quiz.answer;
                    const isWrong = isAnswered && isSelected && option !== quiz.answer;

                    return (
                      <button
                        key={option}
                        className={`option-button ${isCorrect ? "correct" : ""} ${isWrong ? "wrong" : ""} ${isSelected ? "selected" : ""}`}
                        type="button"
                        onClick={() => handleAnswer(option)}
                        disabled={isAnswered || loadingEval}
                      >
                        <span>{optionLetters[index] ?? "•"}.</span>
                        {option}
                      </button>
                    );
                  })}
                </div>

                {loadingEval && (
                  <p style={{ textAlign: "center", padding: "1rem", opacity: 0.7 }}>Evaluating…</p>
                )}

                {evaluation && (
                  <div className="explanation-panel" role="status">
                    <strong>
                      {evaluation.evaluation.correct ? `+${evaluation.gamification?.xp_earned ?? 10} XP earned` : "Not quite!"}
                    </strong>
                    <p>{evaluation.evaluation.feedback}</p>
                    <p style={{ opacity: 0.8, fontSize: "0.92rem" }}>{evaluation.evaluation.explanation}</p>
                    {evaluation.evaluation.improvement_tip && (
                      <p style={{ opacity: 0.75, fontSize: "0.9rem", marginTop: "0.4rem" }}>
                        💡 {evaluation.evaluation.improvement_tip}
                      </p>
                    )}
                  </div>
                )}

                {evaluation && (
                  <div style={{ display: "flex", gap: "0.75rem", marginTop: "1rem" }}>
                    <button
                      className="quiz-primary-button"
                      type="button"
                      onClick={handleNext}
                    >
                      Next Question
                    </button>
                    <button
                      className="quiz-secondary-button"
                      type="button"
                      onClick={handleFinish}
                      style={{ padding: "0.6rem 1.2rem", borderRadius: 8, background: "transparent", border: "1px solid rgba(255,255,255,0.3)", color: "inherit", cursor: "pointer" }}
                    >
                      Finish
                    </button>
                  </div>
                )}
              </>
            ) : null}
          </section>
        )}
      </section>

      <div className="moon-band moon-left" aria-hidden="true" />
      <div className="moon-band moon-right" aria-hidden="true" />
    </main>
  );
}

function ResultCard({
  badgeUnlocked,
  totalCount,
  resultTitle,
  score,
  xpEarned,
  onRetry,
}: Readonly<{
  badgeUnlocked: boolean;
  totalCount: number;
  resultTitle: string;
  score: number;
  xpEarned: number;
  onRetry: () => void;
}>) {
  return (
    <section className="quiz-card result-card" aria-labelledby="result-title">
      <p className="result-kicker">Quest Complete</p>
      <h1 id="result-title">{resultTitle}</h1>
      <div className="score-orb" aria-label={`Score ${score} out of ${totalCount}`}>
        <span>{score}</span>
        <small>/{totalCount}</small>
      </div>
      <div className="reward-grid">
        <span>
          <strong>{xpEarned}</strong>
          XP Earned
        </span>
        <span>
          <strong>{badgeUnlocked ? "Gold" : "Bronze"}</strong>
          Badge
        </span>
      </div>
      <div className="result-actions">
        <button className="quiz-primary-button" type="button" onClick={onRetry}>
          Retry
        </button>
        <Link className="quiz-secondary-button" href="/learn">
          Back to Learn
        </Link>
        <Link className="quiz-secondary-button" href="/career">
          Career Paths
        </Link>
      </div>
    </section>
  );
}
