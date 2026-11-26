# FastAPI bridge for Google ADK

Run from the project root (the directory containing `disney_assistant`):

```powershell
python -m pip install -r api/requirements.txt
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend reads the Gemini key from `disney_assistant/.env` through the ADK environment setup. If your existing ADK run loads dotenv only through its CLI, create a root `.env` or set `GOOGLE_API_KEY` in the shell before starting Uvicorn.

Endpoints: `GET /health`, `POST /api/chat`. This demo intentionally accepts only `mock_mode=true`.
