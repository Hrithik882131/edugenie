import hashlib
import threading
import time
from collections import OrderedDict

from google import genai
from google.genai import types

from config import settings


class GeminiConfigurationError(RuntimeError):
    pass


class GeminiRateLimitError(RuntimeError):
    pass


class GeminiQuotaError(RuntimeError):
    pass


class GeminiGenerationError(RuntimeError):
    pass


# ---------------------------------------------------------
# Simple in-memory cache
# ---------------------------------------------------------

_cache = OrderedDict()
_cache_lock = threading.Lock()


def _cache_key(
    prompt: str,
    system_instruction: str | None,
    temperature: float,
    max_output_tokens: int,
) -> str:
    raw = (
        f"{system_instruction or ''}|"
        f"{prompt}|"
        f"{temperature}|"
        f"{max_output_tokens}|"
        f"{settings.gemini_model}"
    )

    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _get_cached(key: str):
    if not settings.cache_enabled:
        return None

    with _cache_lock:
        if key not in _cache:
            return None

        value = _cache.pop(key)
        _cache[key] = value
        return value


def _save_cache(key: str, value: str):
    if not settings.cache_enabled:
        return

    with _cache_lock:
        _cache[key] = value

        while len(_cache) > settings.cache_size:
            _cache.popitem(last=False)


# ---------------------------------------------------------
# Request cooldown
# ---------------------------------------------------------

_last_request_time = 0.0
_request_lock = threading.Lock()


def _wait_for_cooldown():
    global _last_request_time

    with _request_lock:
        now = time.monotonic()

        elapsed = now - _last_request_time
        remaining = settings.request_cooldown_seconds - elapsed

        if remaining > 0:
            time.sleep(remaining)

        _last_request_time = time.monotonic()


# ---------------------------------------------------------
# Gemini client
# ---------------------------------------------------------

_client = None
_client_lock = threading.Lock()


def get_client() -> genai.Client:
    global _client

    if not settings.gemini_api_key:
        raise GeminiConfigurationError(
            "GEMINI_API_KEY is not configured. "
            "Open .env and add your Gemini API key."
        )

    with _client_lock:
        if _client is None:
            _client = genai.Client(
                api_key=settings.gemini_api_key
            )

        return _client


# ---------------------------------------------------------
# Error detection
# ---------------------------------------------------------

def _classify_gemini_error(exc: Exception) -> Exception:
    message = str(exc).lower()

    # Daily quota / exhausted quota
    quota_words = [
        "quota exceeded",
        "quota_exceeded",
        "daily quota",
        "resource exhausted",
        "limit: 0",
    ]

    if any(word in message for word in quota_words):
        return GeminiQuotaError(
            "Gemini free-tier quota has been reached. "
            "Please wait until the quota resets or use another available "
            "Gemini project/key."
        )

    # Rate limiting
    rate_words = [
        "429",
        "too many requests",
        "rate limit",
        "rate_limit_exceeded",
        "resource_exhausted",
    ]

    if any(word in message for word in rate_words):
        return GeminiRateLimitError(
            "Gemini is rate-limiting this request. "
            "Please wait a few seconds and try again."
        )

    return GeminiGenerationError(
        f"Gemini generation failed: {exc}"
    )


# ---------------------------------------------------------
# Generate text
# ---------------------------------------------------------

def generate_text(
    prompt: str,
    *,
    system_instruction: str | None = None,
    temperature: float = 0.2,
    max_output_tokens: int | None = None,
) -> str:

    # Protect input size
    prompt = prompt[: settings.max_input_chars]

    if max_output_tokens is None:
        max_output_tokens = settings.max_output_tokens

    # Protect output size
    max_output_tokens = min(
        max_output_tokens,
        settings.max_output_tokens,
    )

    # Check cache BEFORE contacting Gemini
    key = _cache_key(
        prompt,
        system_instruction,
        temperature,
        max_output_tokens,
    )

    cached = _get_cached(key)

    if cached is not None:
        return cached

    # Wait between requests
    _wait_for_cooldown()

    client = get_client()

    config = types.GenerateContentConfig(
        temperature=temperature,
        max_output_tokens=max_output_tokens,
        system_instruction=system_instruction,
    )

    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=config,
        )

        text = (response.text or "").strip()

        if not text:
            raise GeminiGenerationError(
                "Gemini returned an empty response."
            )

        # Save result locally.
        # Repeating exactly the same request won't consume API quota.
        _save_cache(key, text)

        return text

    except (
        GeminiConfigurationError,
        GeminiRateLimitError,
        GeminiQuotaError,
        GeminiGenerationError,
    ):
        raise

    except Exception as exc:
        raise _classify_gemini_error(exc) from exc