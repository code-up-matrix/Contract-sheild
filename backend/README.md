# Contract Shield API

FastAPI backend that accepts a PDF or DOCX contract, extracts text, and returns:

- Risk score (0-100)
- Red flags for unlimited liability, broad indemnity, and non-compete clauses
- Plain-English explanations
- Negotiation tips
- Draft negotiation email

## Run locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
