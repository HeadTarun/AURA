"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import soundManager from "@/utils/soundManager";

type QuizQuestion = {
  question: string;
  options: string[];
  answer: string;
  explanation: string;
};

const trackId = 1;
const xpPerCorrect = 10;

const fallbackQuestions: QuizQuestion[] = [
  {
    question: "What is the output of print(2 + 3)?",
    options: ["23", "5", "Error", "None"],
    answer: "5",
    explanation: "Python adds the two numbers first, so print(2 + 3) displays 5.",
  },
  {
    question: "Which symbol starts a comment in Python?",
    options: ["//", "#", "<!--", "/*"],
    answer: "#",
    explanation: "Python uses # for single-line comments.",
  },
  {
    question: "Which value type is True or False?",
    options: ["String", "Integer", "Boolean", "List"],
    answer: "Boolean",
    explanation: "A boolean stores logical values: True or False.",
  },
  {
    question: "What does a loop help you do?",
    options: ["Repeat code", "Delete files", "Rename Python", "Stop variables"],
    answer: "Repeat code",
    explanation: "Loops run the same block of code multiple times.",
  },
];

export default function QuizPage() {
  const [questions, setQuestions] = useState<QuizQuestion[]>(fallbackQuestions);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedOption, setSelectedOption] = useState("");
  const [score, setScore] = useState(0);
  const [isAnswered, setIsAnswered] = useState(false);
  const [loading, setLoading] = useState(true);
  const [submitted, setSubmitted] = useState(false);

  useEffect(() => {
    let active = true;

    async function loadQuiz() {
      try {
        const response = await fetch(`/quiz/${trackId}`);

        if (!response.ok) {
          throw new Error("Using local quiz questions");
        }

        const data = (await response.json()) as QuizQuestion[];

        if (active && data.length > 0) {
          setQuestions(data);
        }
      } catch {
        if (active) {
          setQuestions(fallbackQuestions);
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    }

    loadQuiz();

    return () => {
      active = false;
    };
  }, []);

  const currentQuestion = questions[currentQuestionIndex];
  const progress = Math.round(((currentQuestionIndex + (isAnswered ? 1 : 0)) / questions.length) * 100);
  const xpEarned = score * xpPerCorrect;
  const badgeUnlocked = score === questions.length;
  const optionLetters = ["A", "B", "C", "D"];

  const resultTitle = useMemo(() => {
    if (badgeUnlocked) {
      return "Perfect Clear";
    }

    if (score >= Math.ceil(questions.length * 0.7)) {
      return "Level Passed";
    }

    return "Try Again";
  }, [badgeUnlocked, questions.length, score]);

  function handleAnswer(option: string) {
    if (isAnswered) {
      return;
    }

    setSelectedOption(option);
    setIsAnswered(true);

    if (option === currentQuestion.answer) {
      soundManager.play("success");
      setScore((currentScore) => currentScore + 1);
    } else {
      soundManager.play("error");
    }
  }

  async function submitScore(finalScore: number) {
    try {
      await fetch("/quiz/submit", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          score: finalScore,
          track_id: trackId,
        }),
      });
    } catch {
      // The page remains playable when the backend is not running yet.
    }
  }

  async function handleNext() {
    if (!isAnswered) {
      return;
    }

    if (currentQuestionIndex < questions.length - 1) {
      soundManager.play("click");
      setCurrentQuestionIndex((index) => index + 1);
      setSelectedOption("");
      setIsAnswered(false);
      return;
    }

    soundManager.play("levelup");
    await submitScore(score);
    setSubmitted(true);
  }

  function retryQuiz() {
    soundManager.play("click");
    setCurrentQuestionIndex(0);
    setSelectedOption("");
    setScore(0);
    setIsAnswered(false);
    setSubmitted(false);
  }

  return (
    <main className="quiz-screen">
      <header className="quiz-nav" aria-label="Quiz navigation">
        <Link className="brand" href="/" aria-label="AI Tutor home">
          <span className="brand-coin" aria-hidden="true" />
          <span>AI Tutor</span>
        </Link>

        <Link className="quiz-back-link" href="/learn">
          Back to Learn
        </Link>

        <div className="quiz-nav-stats" aria-label="Quiz progress">
          <span>{xpEarned} XP</span>
          <div className="quiz-progress" aria-label={`${progress}% complete`}>
            <span style={{ width: `${progress}%` }} />
          </div>
          <span>{progress}%</span>
        </div>
      </header>

      <div className="star-field" aria-hidden="true">
        {Array.from({ length: 28 }, (_, index) => (
          <span key={index} className={`star star-${index + 1}`} />
        ))}
      </div>

      <section className="quiz-stage" aria-labelledby="quiz-title">
        <div className="quiz-world" aria-hidden="true">
          <span className="quiz-block block-one" />
          <span className="quiz-block block-two" />
          <span className="quiz-block block-three" />
          <span className="quiz-crystal" />
        </div>

        <div className="assistant-row quiz-assistant" aria-hidden="true">
          <div className="pixel-computer">
            <span className="monitor" />
            <span className="face" />
            <span className="base" />
          </div>
          <div className="speech-bubble">
            Choose your answer and earn XP for the next level :)
          </div>
        </div>

        {submitted ? (
          <ResultCard
            badgeUnlocked={badgeUnlocked}
            questionsLength={questions.length}
            resultTitle={resultTitle}
            score={score}
            xpEarned={xpEarned}
            onRetry={retryQuiz}
          />
        ) : (
          <section className="quiz-card" aria-labelledby="quiz-title" aria-busy={loading}>
            <div className="quiz-card-header">
              <p>Level {currentQuestionIndex + 1}</p>
              <span>{loading ? "Loading..." : `${score}/${questions.length} correct`}</span>
            </div>

            <h1 id="quiz-title">Code Quest</h1>

            <div className="question-panel">
              <p className="question-kicker">Question {currentQuestionIndex + 1}</p>
              <h2>{currentQuestion.question}</h2>
            </div>

            <div className="option-grid" role="list" aria-label="Answer options">
              {currentQuestion.options.map((option, index) => {
                const isSelected = selectedOption === option;
                const isCorrect = isAnswered && option === currentQuestion.answer;
                const isWrong = isAnswered && isSelected && option !== currentQuestion.answer;

                return (
                  <button
                    key={option}
                    className={`option-button ${isCorrect ? "correct" : ""} ${isWrong ? "wrong" : ""} ${
                      isSelected ? "selected" : ""
                    }`}
                    type="button"
                    onClick={() => handleAnswer(option)}
                    disabled={isAnswered}
                  >
                    <span>{optionLetters[index]}.</span>
                    {option}
                  </button>
                );
              })}
            </div>

            {isAnswered ? (
              <div className="explanation-panel" role="status">
                <strong>
                  {selectedOption === currentQuestion.answer ? "+10 XP earned" : "Checkpoint missed"}
                </strong>
                <p>{currentQuestion.explanation}</p>
              </div>
            ) : null}

            <button className="quiz-primary-button" type="button" disabled={!isAnswered} onClick={handleNext}>
              {currentQuestionIndex < questions.length - 1 ? "Next Question" : "Finish Quest"}
            </button>
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
  questionsLength,
  resultTitle,
  score,
  xpEarned,
  onRetry,
}: Readonly<{
  badgeUnlocked: boolean;
  questionsLength: number;
  resultTitle: string;
  score: number;
  xpEarned: number;
  onRetry: () => void;
}>) {
  return (
    <section className="quiz-card result-card" aria-labelledby="result-title">
      <p className="result-kicker">Quest Complete</p>
      <h1 id="result-title">{resultTitle}</h1>
      <div className="score-orb" aria-label={`Score ${score} out of ${questionsLength}`}>
        <span>{score}</span>
        <small>/{questionsLength}</small>
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
        <Link className="quiz-secondary-button" href="/learn/1">
          Next Lesson
        </Link>
      </div>
    </section>
  );
}
