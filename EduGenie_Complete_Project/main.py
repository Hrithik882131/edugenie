from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from api_models import (
    TextRequest,
    LearningPathRequest,
    QAResponse,
    ExplanationResponse,
    QuizResponse,
    SummaryResponse,
    LearningPathResponse,
    ErrorResponse,
)
from qna import answer_question
from explanation_module import explain_topic
from quiz_module import generate_quiz
from summary_module import summarize_text
from learning_path import get_learning_recommendations
from config import settings

BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(
    title="EduGenie - Google Gemini Powered Learning Assistant",
    description="AI-powered educational assistant built with FastAPI and Gemini.",
    version="1.0.0",
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"app_name": settings.app_name},
    )


@app.get("/health")
async def health():
    return {
        "status": "ok",
        "app": settings.app_name,
        "gemini_configured": bool(settings.gemini_api_key),
        "model": settings.gemini_model,
        "explanation_provider": settings.explanation_provider,
    }


@app.post("/qa", response_model=QAResponse, responses={500: {"model": ErrorResponse}})
async def qa(payload: TextRequest):
    try:
        answer = answer_question(payload.text)
        return QAResponse(answer=answer)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/explain", response_model=ExplanationResponse, responses={500: {"model": ErrorResponse}})
async def explain(payload: TextRequest):
    try:
        explanation = explain_topic(payload.text)
        return ExplanationResponse(explanation=explanation)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/quiz", response_model=QuizResponse, responses={500: {"model": ErrorResponse}})
async def quiz(payload: TextRequest):
    try:
        result = generate_quiz(payload.text)
        return result
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/summarize", response_model=SummaryResponse, responses={500: {"model": ErrorResponse}})
async def summarize(payload: TextRequest):
    try:
        summary = summarize_text(payload.text)
        return SummaryResponse(summary=summary)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post(
    "/learn/recommendations",
    response_model=LearningPathResponse,
    responses={500: {"model": ErrorResponse}},
)
async def learning_recommendations(payload: LearningPathRequest):
    try:
        result = get_learning_recommendations(
            topic=payload.topic,
            level=payload.level,
            goal=payload.goal,
        )
        return LearningPathResponse(
            topic=payload.topic,
            level=payload.level,
            recommendations=result,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
