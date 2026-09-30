from pydantic import BaseModel, Field

from config import settings
from gemini_client import (
    get_client,
    GeminiGenerationError,
    GeminiRateLimitError,
    GeminiQuotaError,
)


class QuizQuestionSchema(BaseModel):
    question: str
    options: list[str] = Field(
        min_length=4,
        max_length=4
    )
    correct_answer: str
    explanation: str


class QuizSchema(BaseModel):
    questions: list[QuizQuestionSchema] = Field(
        min_length=3,
        max_length=3
    )


def generate_quiz(source_text: str):

    source_text = source_text[:settings.max_input_chars]

    client = get_client()

    prompt = f"""
Create exactly 3 MCQ questions from this educational content.

Rules:
- Exactly 3 questions.
- Exactly 4 options per question.
- Only one correct answer.
- correct_answer must exactly match one option.
- Keep explanations very short.
- Use only information from the supplied content.

Content:

{source_text}
"""

    try:
        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config={
                "temperature": 0.2,
                "max_output_tokens": 900,
                "response_mime_type": "application/json",
                "response_schema": QuizSchema,
            },
        )

        if getattr(response, "parsed", None) is not None:
            return response.parsed

        return QuizSchema.model_validate_json(
            response.text
        )

    except (
        GeminiRateLimitError,
        GeminiQuotaError,
        GeminiGenerationError,
    ):
        raise

    except Exception as exc:
        message = str(exc).lower()

        if "429" in message or "resource exhausted" in message:
            raise GeminiRateLimitError(
                "Gemini is temporarily rate-limiting the quiz request. "
                "Please wait and try again."
            ) from exc

        raise GeminiGenerationError(
            f"Quiz generation failed: {exc}"
        ) from exc