# CareerOS

CareerOS is a local AI-assisted job search workspace for finding jobs, tracking applications, comparing job descriptions against your resume, and automating parts of the application workflow.

The current codebase is a FastAPI backend with a Vite React frontend. The backend exposes JWT-protected APIs for authentication, profile management, job scraping, job tracking, and the application automation pipeline. The frontend provides the dashboard, sign-in/register flow, profile editor, and job tracker UI.

## Current Architecture

### Backend

- FastAPI app entrypoint: `backend/main.py`
- API routers: `backend/api/auth.py`, `backend/api/profile.py`, `backend/api/jobs.py`
- Database models: `backend/db/models.py`
- Database session: local SQLite database at `database.db`
- Authentication: JWT bearer tokens using `python-jose`; passwords are hashed with `bcrypt`
- CORS: local frontend origins are allowed by default, including dynamic `localhost` and `127.0.0.1` ports
- AI workflow: LangGraph pipeline in `backend/graph/pipeline.py`
- LLM access: Gemini client in `backend/agents/llm_client.py`
- Browser automation: Playwright-based crawlers and application agent

### Frontend

- Vite + React + TypeScript app in `frontend/`
- API client: `frontend/src/lib/api.ts`
- Auth state: `frontend/src/context/AuthContext.tsx`
- Job state: `frontend/src/context/JobsContext.tsx`
- Pages: dashboard, login/register, job tracker, profile
- Styling: custom CSS in `frontend/src/index.css`

## Features

- Register, sign in, and persist sessions with JWT tokens
- Maintain a profile and base resume text
- Scrape jobs from LinkedIn and Indeed crawler modules
- Track jobs and application status in SQLite
- Analyze job descriptions against your profile using Gemini-powered agents
- Generate optimized resume content and PDFs with Playwright
- Run an application automation pipeline through LangGraph

## Requirements

### Backend

Python dependencies are listed in `requirements.txt`. The file now contains direct backend requirements for the current architecture instead of a full virtualenv freeze.

Important runtime pieces:

- `fastapi`, `uvicorn`, `python-multipart`
- `sqlmodel` with SQLite
- `bcrypt` and `python-jose` for auth
- `pydantic-settings` and `.env` configuration
- `google-genai`, `langgraph`
- `playwright`, `beautifulsoup4`

`passlib` is no longer required. Password hashing uses `bcrypt` directly, and passwords longer than bcrypt's 72-byte input limit are rejected cleanly.

### Frontend

Frontend dependencies are managed separately in `frontend/package.json` with npm. Key packages include React, Vite, axios, react-router, lucide-react, framer-motion, and react-hot-toast.

## Environment

Create or update `.env` in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key
SECRET_KEY=replace_with_a_long_random_secret
```

Optional values:

```env
ACCESS_TOKEN_EXPIRE_MINUTES=10080
BACKEND_CORS_ORIGIN_REGEX=http://(localhost|127\.0\.0\.1):\d+
```

If you need an explicit CORS allow-list through environment variables, provide it as JSON:

```env
BACKEND_CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173"]
```

For the frontend, create `frontend/.env` only when the backend is not running at the default URL:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

## Setup

### 1. Backend

From the project root:

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
uvicorn backend.main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

FastAPI docs are available at:

```text
http://127.0.0.1:8000/docs
```

### 2. Frontend

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Vite will print the frontend URL, usually:

```text
http://localhost:5173
```

## Authentication Notes

The frontend signs in through:

```text
POST /api/auth/token
```

That endpoint expects OAuth form data with `username` and `password`. The frontend maps the email field to `username` automatically.

Registration uses:

```text
POST /api/auth/register
```

Both successful login and registration return a bearer token. The frontend stores it in `localStorage` and attaches it to protected requests.

## Verification

Backend smoke checks can be run with:

```powershell
.\venv\Scripts\python.exe -m pytest
```

At the moment, there are no pytest test cases collected. `test_agents.py` is a manual agent smoke script, not a pytest module.

Frontend build verification:

```powershell
cd frontend
npm.cmd run build
```

Use `npm.cmd` on Windows if PowerShell blocks `npm.ps1` because of execution policy settings.

## Project Layout

```text
CareerOS/
  backend/
    agents/          AI, crawler, resume, cover letter, and application agents
    api/             FastAPI routers
    core/            settings, logging, auth/security helpers
    db/              SQLModel models and session setup
    graph/           LangGraph application pipeline
    utils/           Playwright helper utilities
    main.py          FastAPI app entrypoint
  frontend/
    src/             Vite React application
    package.json     frontend dependencies and scripts
  logs/              backend log output
  database.db        local SQLite database
  requirements.txt   backend Python dependencies
  README.md          project documentation
```

## Responsible Use

CareerOS uses browser automation for scraping and form interaction. Some job platforms restrict automated access or submissions in their terms of service. Use the automation features carefully and responsibly.
