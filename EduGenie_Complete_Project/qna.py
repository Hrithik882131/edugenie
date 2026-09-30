from gemini_client import generate_text


SYSTEM = """
You are EduGenie, a simple educational assistant.

Answer the student's question accurately and clearly.

Rules:
- Use simple English.
- Keep the answer short.
- Prefer 4 to 7 short points when suitable.
- Do not unnecessarily repeat the question.
- Do not generate long essays unless requested.
"""


def answer_question(question: str) -> str:

    prompt = f"""
Student question:

{question}

Give a concise educational answer.
"""

    return generate_text(
        prompt,
        system_instruction=SYSTEM,
        temperature=0.2,
        max_output_tokens=500,
    )