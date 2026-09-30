from fastapi.testclient import TestClient
import main

client = TestClient(main.app)


def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "EduGenie" in response.text


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_qa_validation(monkeypatch):
    monkeypatch.setattr(main, "answer_question", lambda text: "Mock answer")
    response = client.post("/qa", json={"text": "What is Python?"})
    assert response.status_code == 200
    assert response.json()["answer"] == "Mock answer"


def test_explain_validation(monkeypatch):
    monkeypatch.setattr(main, "explain_topic", lambda text: "Mock explanation")
    response = client.post("/explain", json={"text": "Explain AI"})
    assert response.status_code == 200
    assert response.json()["explanation"] == "Mock explanation"


def test_summary_validation(monkeypatch):
    monkeypatch.setattr(main, "summarize_text", lambda text: "Mock summary")
    response = client.post("/summarize", json={"text": "Long educational passage"})
    assert response.status_code == 200
    assert response.json()["summary"] == "Mock summary"


def test_learning_path_validation(monkeypatch):
    monkeypatch.setattr(
        main,
        "get_learning_recommendations",
        lambda topic, level, goal: "Mock learning path",
    )
    response = client.post(
        "/learn/recommendations",
        json={"topic": "SQL", "level": "Beginner", "goal": "Learn SQL"},
    )
    assert response.status_code == 200
    assert response.json()["recommendations"] == "Mock learning path"


def test_quiz_validation(monkeypatch):
    fake = {
        "questions": [
            {
                "question": "Q1",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "A",
                "explanation": "Because A is correct.",
            },
            {
                "question": "Q2",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "B",
                "explanation": "Because B is correct.",
            },
            {
                "question": "Q3",
                "options": ["A", "B", "C", "D"],
                "correct_answer": "C",
                "explanation": "Because C is correct.",
            },
        ]
    }
    monkeypatch.setattr(main, "generate_quiz", lambda text: fake)
    response = client.post("/quiz", json={"text": "Python basics"})
    assert response.status_code == 200
    assert len(response.json()["questions"]) == 3
