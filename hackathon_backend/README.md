# Evidence Extraction Backend

Minimal FastAPI backend for the hackathon's evidence extraction / AI pipeline.

## Run

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env  # Windows: copy .env.example .env
uvicorn app.main:app --reload
```

API: `http://127.0.0.1:8000`
Docs: `http://127.0.0.1:8000/docs`

## Optional LLM

Set `OPENAI_API_KEY` in `.env`. If it is absent, deterministic extraction still works.

## Test

```bash
pytest -q
```

## Endpoints

- `GET /health`
- `POST /api/evidence/analyze` with JSON `{ "text": "...", "evidence_source": "message" }`
- `POST /api/evidence/analyze-file` with multipart `file`

The output is a Pydantic-validated `ExtractionResult` intended to be consumed by the timeline, conflict-detection, privacy, and frontend components.
