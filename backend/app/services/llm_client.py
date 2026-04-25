import json
import logging
import os
import time
from typing import Any

import google.generativeai as genai
from groq import Groq
<<<<<<< HEAD
import dotenv

dotenv.load_dotenv()
=======

>>>>>>> 7112dbfcf0f7cbb6a023bd5e7a3412fc2eb4431b
GEMINI_MODEL = "gemini-2.5-flash"
GROQ_MODEL = "llama-3.3-70b-versatile"
TIMEOUT_SEC = 3

_logger = logging.getLogger(__name__)
_gemini_configured = False
_groq_client: Groq | None = None


def _parse_json_object(raw_text: str) -> dict[str, Any]:
    parsed = json.loads(raw_text)
    if not isinstance(parsed, dict):
        raise ValueError("LLM response is not a JSON object")
    return parsed


def _configure_gemini() -> None:
    global _gemini_configured
    if _gemini_configured:
        return
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        raise KeyError("GEMINI_API_KEY is not set")
    genai.configure(api_key=gemini_key)
    _gemini_configured = True


def _get_groq_client() -> Groq:
    global _groq_client
    if _groq_client is not None:
        return _groq_client
    groq_key = os.getenv("GROQ_API_KEY")
    if not groq_key:
        raise KeyError("GROQ_API_KEY is not set")
    _groq_client = Groq(api_key=groq_key)
    return _groq_client


def call_llm(prompt: str, fallback: dict[str, Any], max_tokens: int = 1024) -> dict[str, Any]:
    """
    Primary: Gemini 2.5 Flash
    Fallback: Groq Llama 3.3 70B
    Final fallback: return `fallback` dict unchanged.

    Gemini is called with response_mime_type="application/json" to force JSON.
    Groq is called with response_format={"type": "json_object"}.
    """
    try:
        _configure_gemini()
        model = genai.GenerativeModel(GEMINI_MODEL)
        start = time.monotonic()
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                max_output_tokens=max_tokens,
                response_mime_type="application/json",
            ),
        )
        elapsed = time.monotonic() - start
        if elapsed > TIMEOUT_SEC:
            raise TimeoutError(f"Gemini took {elapsed:.1f}s (limit {TIMEOUT_SEC}s)")
        text = (response.text or "").strip()
        return _parse_json_object(text)
    except (KeyError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
        _logger.warning("Gemini unavailable; trying Groq. reason=%s", exc)
    except Exception as exc:
        _logger.warning("Gemini request failed; trying Groq. reason=%s", exc)

    try:
        groq_client = _get_groq_client()
        response = groq_client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content or ""
        return _parse_json_object(content.strip())
    except (KeyError, ValueError, json.JSONDecodeError) as exc:
        _logger.warning("Groq unavailable; using fallback. reason=%s", exc)
    except Exception as exc:
        _logger.warning("Groq request failed; using fallback. reason=%s", exc)

    return fallback
