import json
import logging
import os
from typing import Any

try:
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - dependency may be absent in minimal envs
    load_dotenv = None

try:
    import google.generativeai as genai
except ImportError:  # pragma: no cover
    genai = None

try:
    from groq import Groq
except ImportError:  # pragma: no cover
    Groq = None

if load_dotenv is not None:
    load_dotenv()

GEMINI_MODEL = "gemini-2.5-flash"
GROQ_MODEL = "llama-3.3-70b-versatile"

_logger = logging.getLogger(__name__)
_gemini_configured = False
_groq_client: Any | None = None


def _parse_json_object(raw_text: str) -> dict[str, Any]:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`").replace("json\n", "", 1).strip()
    parsed = json.loads(cleaned)
    if not isinstance(parsed, dict):
        raise ValueError("LLM response is not a JSON object")
    return parsed


def _configure_gemini() -> None:
    global _gemini_configured
    if _gemini_configured:
        return
    if genai is None:
        raise RuntimeError("google-generativeai is not installed")
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise KeyError("GEMINI_API_KEY is not set")
    genai.configure(api_key=gemini_key)
    _gemini_configured = True


def _get_groq_client() -> Any:
    global _groq_client
    if _groq_client is not None:
        return _groq_client
    if Groq is None:
        raise RuntimeError("groq is not installed")
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise KeyError("GROQ_API_KEY is not set")
    _groq_client = Groq(api_key=groq_key)
    return _groq_client


def call_llm(
    prompt: str, fallback: dict[str, Any], max_tokens: int = 1024
) -> dict[str, Any]:
    try:
        _configure_gemini()
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=max_tokens,
                response_mime_type="application/json",
            ),
        )
        return _parse_json_object(response.text or "")
    except Exception as exc:
        _logger.warning("Gemini unavailable; trying Groq. reason=%s", exc)

    try:
        groq_client = _get_groq_client()
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or ""
        return _parse_json_object(content)
    except Exception as exc:
        _logger.warning("Groq unavailable; using static fallback. reason=%s", exc)

    return dict(fallback)
