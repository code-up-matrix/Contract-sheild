from __future__ import annotations

import re
from io import BytesIO
from pathlib import Path
from typing import Any

import docx
import pdfplumber
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Contract Shield API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_SUMMARY_CHARS = 1000


def extract_text_from_pdf(contents: bytes) -> str:
    text_chunks: list[str] = []
    with pdfplumber.open(BytesIO(contents)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            if page_text.strip():
                text_chunks.append(page_text)
    return "\n".join(text_chunks).strip()


def extract_text_from_docx(contents: bytes) -> str:
    document = docx.Document(BytesIO(contents))
    paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
    return "\n".join(paragraphs).strip()


def summarize_text(text: str, max_chars: int = MAX_SUMMARY_CHARS) -> str:
    normalized = re.sub(r"\s+", " ", text).strip()
    if len(normalized) <= max_chars:
        return normalized
    summary = normalized[:max_chars].rsplit(" ", 1)[0]
    return f"{summary}…"


def detect_patterns(text: str) -> dict[str, Any]:
    lowered = text.lower()

    patterns = {
        "unlimited_liability": {
            "weight": 35,
            "label": "Unlimited liability",
            "plain_explanation": "The contract appears to make you responsible for potentially unlimited losses.",
            "negotiation_tip": "Request a liability cap tied to fees paid under the agreement.",
            "email_line": "Could we add a reasonable cap on liability (for example, total fees paid under this contract)?",
            "regexes": [
                r"unlimited liability",
                r"liability\s+shall\s+not\s+be\s+limited",
                r"without\s+limit(?:ation)?\s+of\s+liability",
                r"liable\s+for\s+any\s+and\s+all\s+damages",
            ],
        },
        "broad_indemnity": {
            "weight": 30,
            "label": "Broad indemnity",
            "plain_explanation": "You may be required to cover very broad third-party claims and costs.",
            "negotiation_tip": "Narrow indemnity to direct losses caused by your proven breach or negligence.",
            "email_line": "Can we narrow indemnity so it only applies to claims directly caused by my breach or negligence?",
            "regexes": [
                r"indemnify(?:,?\s+defend\s+and\s+hold\s+harmless)?",
                r"any\s+and\s+all\s+claims",
                r"including\s+consequential\s+damages",
                r"at\s+its\s+sole\s+expense",
            ],
        },
        "non_compete": {
            "weight": 25,
            "label": "Broad non-compete",
            "plain_explanation": "The non-compete language may limit your ability to work with other clients.",
            "negotiation_tip": "Limit non-compete scope by geography, duration, and specific competitor list.",
            "email_line": "Could we narrow the non-compete by reducing duration and limiting it to named direct competitors?",
            "regexes": [
                r"non-?compete",
                r"shall\s+not\s+engage\s+in\s+any\s+business\s+that\s+competes",
                r"for\s+a\s+period\s+of\s+\d+\s+(?:years|months)",
                r"any\s+client\s+or\s+prospective\s+client",
            ],
        },
    }

    findings: list[dict[str, str | int]] = []
    risk_score = 10

    for key, config in patterns.items():
        matched_snippets = []
        for regex in config["regexes"]:
            match = re.search(regex, lowered)
            if match:
                start = max(0, match.start() - 60)
                end = min(len(text), match.end() + 90)
                snippet = text[start:end].replace("\n", " ").strip()
                matched_snippets.append(snippet)

        if matched_snippets:
            risk_score += config["weight"]
            findings.append(
                {
                    "key": key,
                    "label": config["label"],
                    "severity": min(100, config["weight"] + 30),
                    "plain_explanation": config["plain_explanation"],
                    "negotiation_tip": config["negotiation_tip"],
                    "email_line": config["email_line"],
                    "snippet": matched_snippets[0],
                }
            )

    risk_score = min(100, risk_score)

    negotiation_tips = [finding["negotiation_tip"] for finding in findings]
    email_lines = [finding["email_line"] for finding in findings]

    draft_email = (
        "Hi [Client Name],\n\n"
        "Thanks for sharing the agreement. I reviewed the terms and would like to align on a few clauses before signing:\n"
        + "\n".join([f"- {line}" for line in email_lines])
        + "\n\nI’m confident these adjustments will keep the project fair and low-risk for both sides.\n\n"
        "Best,\n[Your Name]"
        if email_lines
        else "Hi [Client Name],\n\nThanks for sending the agreement. I reviewed it and I’m comfortable moving forward as written.\n\nBest,\n[Your Name]"
    )

    return {
        "risk_score": risk_score,
        "red_flags": findings,
        "negotiation_tips": negotiation_tips,
        "draft_email": draft_email,
    }


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze")
async def analyze_contract(file: UploadFile = File(...)) -> dict[str, Any]:
    extension = Path(file.filename or "").suffix.lower()
    if extension not in {".pdf", ".docx"}:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported.")

    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    try:
        if extension == ".pdf":
            extracted_text = extract_text_from_pdf(contents)
        else:
            extracted_text = extract_text_from_docx(contents)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"Failed to parse file: {exc}") from exc

    if not extracted_text:
        raise HTTPException(status_code=400, detail="No extractable text found in the contract.")

    analysis = detect_patterns(extracted_text)
    return {
        "filename": file.filename,
        "summary": summarize_text(extracted_text),
        "extracted_text_length": len(extracted_text),
        **analysis,
    }
