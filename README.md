# Contract Shield MVP

Contract Shield is a minimal two-service app for freelancers to upload contracts and get heuristic legal-risk guidance.

## What it does

- Upload PDF or DOCX contracts in a Next.js UI.
- FastAPI extracts text using:
  - `pdfplumber` for PDF
  - `python-docx` for DOCX
- Returns:
  - risk score (0-100)
  - key red flags
  - plain-English explanations
  - negotiation tips
  - draft negotiation email
- Highlights these risk categories:
  - unlimited liability
  - broad indemnity
  - non-compete clauses
- Summarizes extracted text in the UI.

> This is heuristic analysis and not legal advice.

## Project structure

- `frontend/` - Next.js MVP web app
- `backend/` - FastAPI analysis API

## Local development

### 1) Start API

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2) Start web app

```bash
cd frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

Open `http://localhost:3000`.

## Deploy to DigitalOcean App Platform

Deploy as **separate services**:

1. API service from `backend/do-app.yaml`
2. Web service from `frontend/do-app.yaml`

Update `github.repo` and the frontend `NEXT_PUBLIC_API_URL` value before deploy.
