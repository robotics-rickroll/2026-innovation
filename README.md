# Rickroll Artifact Classification MVP

## Overview
Public users can browse artifacts and AI classifications, while archaeologists log in to submit artifacts, run classification, and override results. Location privacy is enforced by storing and returning only rounded coordinates.

## Stack
- Backend: FastAPI + SQLAlchemy + SQLite (swap-ready for Postgres)
- Frontend: React + TypeScript + Vite + React Router
- Auth: JWT for archaeologists
- AI: Mock/OpenAI/Gemini providers

## Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python seed.py
uvicorn app.main:app --reload
```

Backend runs at `http://localhost:8000`.

### Run backend tests
```bash
cd backend
pytest
```

## Frontend Setup
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend runs at `http://localhost:5173`.

### Run frontend tests
```bash
cd frontend
npm run test
```

## Seed Data
`backend/seed.py` creates a demo archaeologist user and a sample artifact.
- Email: `arch@example.com`
- Password: `password`

## Environment Variables
Backend (`backend/.env`):
- `DATABASE_URL` (default `sqlite:///./app.db`)
- `SECRET_KEY`
- `ACCESS_TOKEN_EXPIRE_MINUTES`
- `AI_PROVIDER` (`mock|openai|gemini`)
- `OPENAI_API_KEY`
- `GEMINI_API_KEY`
- `CORS_ORIGINS`
- `UPLOAD_DIR`

Frontend (`frontend/.env`):
- `VITE_API_URL` (default `http://localhost:8000/api`)

## Docker (optional)
```bash
docker-compose up
```

## Notes
- Public endpoints never return raw latitude/longitude.
- `POST /api/artifacts/{id}/classify` uses the configured AI provider. If no keys are set, `mock` is used.
