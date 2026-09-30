# EduGenie — Google Gemini Powered Learning Assistant

EduGenie is a lightweight AI learning assistant based on the supplied project documentation. It provides:

- Question answering
- Beginner-friendly concept explanation
- 3-question MCQ generation with 4 options each
- Educational text summarization
- Personalized beginner-to-advanced learning paths
- A responsive HTML/CSS/JavaScript frontend
- REST APIs using FastAPI
- Optional local LaMini-Flan-T5 explanation mode

## Project structure

```text
EduGenie/
├── main.py
├── config.py
├── gemini_client.py
├── api_models.py
├── explanation_module.py
├── qna.py
├── quiz_module.py
├── summary_module.py
├── learning_path.py
├── requirements.txt
├── requirements-local.txt
├── .env.example
├── .gitignore
├── pytest.ini
├── README.md
├── templates/
│   └── index.html
├── static/
│   ├── style.css
│   └── app.js
└── tests/
    └── test_api.py
```

## 1. Install Python

Use Python 3.10 or newer.

Check:

```bash
python --version
```

On some Windows installations you may need:

```bash
py --version
```

## 2. Open the project in VS Code

Extract the `EduGenie` folder and open that folder in VS Code.

Recommended VS Code extension:
- Python by Microsoft

## 3. Create a virtual environment

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Windows CMD

```cmd
python -m venv .venv
.venv\Scripts\activate
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Configure Gemini

Copy `.env.example` to `.env`.

Windows:

```powershell
copy .env.example .env
```

macOS/Linux:

```bash
cp .env.example .env
```

Open `.env` and replace:

```env
GEMINI_API_KEY=PASTE_YOUR_API_KEY_HERE
```

with your own Gemini API key.

Do not commit `.env` to GitHub. It is already ignored by `.gitignore`.

## 6. Run the application

```bash
uvicorn main:app --reload
```

Open:

```text
http://127.0.0.1:8000
```

The FastAPI API documentation is also available at:

```text
http://127.0.0.1:8000/docs
```

## 7. Test the application

### Browser test

1. Select "Ask a Question".
2. Enter: `What is an operating system?`
3. Click Generate.

Then test:
- Explain a Topic
- Generate Quiz
- Summarize Text
- Recommend Learning Path

### API health test

Open:

```text
http://127.0.0.1:8000/health
```

Expected shape:

```json
{
  "status": "ok",
  "app": "EduGenie",
  "gemini_configured": true,
  "model": "gemini-3.8-flash",
  "explanation_provider": "gemini"
}
```

### Automated tests

Install pytest if it is not already installed:

```bash
pip install pytest
```

Run:

```bash
pytest
```

The tests mock AI responses, so they do not spend Gemini API quota.

## 8. Optional local LaMini explanation mode

The supplied documentation proposes LaMini-Flan-T5-783M for the explanation module.

To enable it:

```bash
pip install -r requirements-local.txt
```

Then change `.env`:

```env
EXPLANATION_PROVIDER=local
```

The model will be downloaded from Hugging Face the first time it is used. CPU inference can be slower than Gemini. If the local model cannot load and a Gemini API key is configured, EduGenie falls back to Gemini.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Web application |
| GET | `/health` | Health/configuration check |
| POST | `/qa` | Question answering |
| POST | `/explain` | Concept explanation |
| POST | `/quiz` | 3 MCQs with 4 options |
| POST | `/summarize` | Text summarization |
| POST | `/learn/recommendations` | Personalized learning path |

## Example API requests

### Q&A

```bash
curl -X POST http://127.0.0.1:8000/qa \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"What is an algorithm?\"}"
```

### Explain

```bash
curl -X POST http://127.0.0.1:8000/explain \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Explain inheritance in Java.\"}"
```

### Quiz

```bash
curl -X POST http://127.0.0.1:8000/quiz \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Python is a high-level programming language used for web development, automation and data science.\"}"
```

### Summary

```bash
curl -X POST http://127.0.0.1:8000/summarize \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Paste a long educational passage here.\"}"
```

### Learning path

```bash
curl -X POST http://127.0.0.1:8000/learn/recommendations \
  -H "Content-Type: application/json" \
  -d "{\"topic\":\"SQL\",\"level\":\"Beginner\",\"goal\":\"Learn SQL for data analysis\"}"
```

## Troubleshooting

### "GEMINI_API_KEY is not configured"

Make sure:
1. `.env` exists in the project root.
2. The variable is named exactly `GEMINI_API_KEY`.
3. You restarted Uvicorn after changing `.env`.

### Gemini model error

Set `GEMINI_MODEL` in `.env` to a model available to your Gemini API account.

### Port already in use

Run:

```bash
uvicorn main:app --reload --port 8001
```

Then open:

```text
http://127.0.0.1:8001
```

### PowerShell blocks activation

You can use CMD instead, or run:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Then activate `.venv`.

## Security notes

- Never put your Gemini API key in frontend JavaScript.
- Keep the key in `.env` on the backend.
- Do not commit `.env`.
- AI-generated answers can contain mistakes; use EduGenie as a learning assistant and verify important academic information.

## Architecture

```text
Browser
   |
   | HTTP POST
   v
FastAPI (main.py)
   |
   +--> qna.py --------------------+
   +--> explanation_module.py -----+
   +--> quiz_module.py ------------+--> Gemini API
   +--> summary_module.py ---------+
   +--> learning_path.py ----------+
   |
   v
HTML + CSS + JavaScript
```
