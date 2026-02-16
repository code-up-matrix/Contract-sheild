# Contract Shield — Codex Agent Instructions

## Goal (MVP Day 1)
Build a monorepo with:
- apps/api: FastAPI service exposing:
  - GET /health -> {ok:true}
  - POST /upload (multipart file PDF/DOCX) -> {doc_id, filename, chars, preview_text}
- apps/web: Next.js app that uploads a PDF/DOCX and displays preview_text in the UI.

## Constraints
- Keep it minimal: no DB, no auth, no Stripe yet.
- Must run locally with two commands (api + web).
- Must be deployable to DigitalOcean App Platform using Dockerfiles.
- Add clear README with env vars.

## Acceptance Criteria
- `curl <api>/health` returns ok:true
- Uploading a sample PDF/DOCX returns JSON with preview_text (first ~800 chars)
- Web UI can upload and show preview in the same page
- CORS allowed from WEB_ORIGIN
- Includes Dockerfile for api
- Web can be deployed as Node build/run# Contract-sheild
