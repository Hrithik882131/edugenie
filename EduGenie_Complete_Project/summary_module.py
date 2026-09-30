from gemini_client import generate_text


SYSTEM = """
You are EduGenie, an educational summarization assistant.

Rules:
- Keep the summary short.
- Preserve important facts.
- Use simple English.
- Do not add information that is not in the input.
- Prefer bullet points.
"""


def summarize_text(text: str) -> str:

    prompt = f"""
Summarize this educational text for quick revision:

{text}

Return:
1. Short overview
2. Main points
3. Important terms
"""

    return generate_text(
        prompt,
        system_instruction=SYSTEM,
        temperature=0.2,
        max_output_tokens=600,
    )