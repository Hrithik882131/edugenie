from pydantic import BaseModel, Field, field_validator


class TextRequest(BaseModel):
    text: str = Field(..., min_length=2, max_length=30000)

    @field_validator("text")
    @classmethod
    def validate_text(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Input must contain at least 2 characters.")
        return value


class LearningPathRequest(BaseModel):
    topic: str = Field(..., min_length=2, max_length=500)
    level: str = Field(default="Beginner", max_length=50)
    goal: str = Field(default="Understand the topic and build a strong foundation.", max_length=500)

    @field_validator("topic", "level", "goal")
    @classmethod
    def strip_fields(cls, value: str) -> str:
        return value.strip()


class QAResponse(BaseModel):
    answer: str


class ExplanationResponse(BaseModel):
    explanation: str


class QuizQuestion(BaseModel):
    question: str
    options: list[str] = Field(..., min_length=4, max_length=4)
    correct_answer: str
    explanation: str


class QuizResponse(BaseModel):
    questions: list[QuizQuestion] = Field(..., min_length=3, max_length=3)


class SummaryResponse(BaseModel):
    summary: str


class LearningPathResponse(BaseModel):
    topic: str
    level: str
    recommendations: str


class ErrorResponse(BaseModel):
    detail: str
