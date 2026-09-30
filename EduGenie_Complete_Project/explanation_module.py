from functools import lru_cache

from config import settings
from gemini_client import generate_text


def _gemini_explanation(topic: str) -> str:
    prompt = f"""Explain the following topic for a beginner:

{topic}

Use this format:
1. Simple definition
2. How it works
3. Easy example
4. Key points

Keep it clear, concise, and educational."""
    return generate_text(
        prompt,
        system_instruction="You are EduGenie. Explain difficult concepts in very simple language.",
        temperature=0.35,
        max_output_tokens=1200,
    )


@lru_cache(maxsize=1)
def _load_local_model():
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(settings.local_explanation_model)
    model = AutoModelForSeq2SeqLM.from_pretrained(settings.local_explanation_model)
    return tokenizer, model


def _local_explanation(topic: str) -> str:
    import torch

    tokenizer, model = _load_local_model()
    prompt = (
        "Explain this educational topic simply for a beginner. "
        "Use short sentences and one easy example:\n\n"
        f"{topic}"
    )
    inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=180,
            num_beams=4,
            early_stopping=True,
        )
    return tokenizer.decode(output[0], skip_special_tokens=True).strip()


def explain_topic(topic: str) -> str:
    provider = settings.explanation_provider.lower().strip()

    if provider == "local":
        try:
            return _local_explanation(topic)
        except Exception:
            # A local model is optional. If it cannot load, use Gemini when configured.
            if settings.gemini_api_key:
                return _gemini_explanation(topic)
            raise

    return _gemini_explanation(topic)
