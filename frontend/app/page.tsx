"use client";

import { FormEvent, useMemo, useState } from "react";

type RedFlag = {
  key: string;
  label: string;
  severity: number;
  plain_explanation: string;
  negotiation_tip: string;
  email_line: string;
  snippet: string;
};

type AnalysisResponse = {
  filename: string;
  summary: string;
  extracted_text_length: number;
  risk_score: number;
  red_flags: RedFlag[];
  negotiation_tips: string[];
  draft_email: string;
};

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Home() {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null);

  const riskLevel = useMemo(() => {
    if (!analysis) return "";
    if (analysis.risk_score >= 70) return "High";
    if (analysis.risk_score >= 40) return "Medium";
    return "Low";
  }, [analysis]);

  async function onSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!file) {
      setError("Please choose a PDF or DOCX contract.");
      return;
    }

    setLoading(true);
    setError(null);
    setAnalysis(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.detail ?? "Analysis failed.");
      }

      setAnalysis(data as AnalysisResponse);
    } catch (submitError) {
      const message = submitError instanceof Error ? submitError.message : "Unexpected error.";
      setError(message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="container">
      <section className="card">
        <h1>Contract Shield</h1>
        <p className="subtitle">
          Upload a freelance contract (PDF/DOCX) to detect unlimited liability, broad indemnity, and
          non-compete risks.
        </p>

        <form onSubmit={onSubmit} className="upload-form">
          <input
            type="file"
            accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            onChange={(event) => setFile(event.target.files?.[0] ?? null)}
          />
          <button type="submit" disabled={loading}>
            {loading ? "Analyzing..." : "Analyze Contract"}
          </button>
        </form>

        {error && <p className="error">{error}</p>}
      </section>

      {analysis && (
        <section className="results">
          <article className="card">
            <h2>Risk Summary</h2>
            <p>
              <strong>Contract:</strong> {analysis.filename}
            </p>
            <p>
              <strong>Risk score:</strong> {analysis.risk_score}/100 ({riskLevel})
            </p>
            <p>
              <strong>Extracted length:</strong> {analysis.extracted_text_length.toLocaleString()} characters
            </p>
            <h3>Extracted Text Summary</h3>
            <p>{analysis.summary}</p>
          </article>

          <article className="card">
            <h2>Red Flags</h2>
            {analysis.red_flags.length === 0 ? (
              <p>No major red flags detected by current heuristics.</p>
            ) : (
              <ul>
                {analysis.red_flags.map((flag) => (
                  <li key={flag.key}>
                    <h3>
                      {flag.label} (Severity {flag.severity}/100)
                    </h3>
                    <p>{flag.plain_explanation}</p>
                    <p>
                      <strong>Matched snippet:</strong> “{flag.snippet}”
                    </p>
                    <p>
                      <strong>Negotiation tip:</strong> {flag.negotiation_tip}
                    </p>
                  </li>
                ))}
              </ul>
            )}
          </article>

          <article className="card">
            <h2>Negotiation Assist</h2>
            <h3>Suggested Talking Points</h3>
            <ul>
              {analysis.negotiation_tips.length > 0 ? (
                analysis.negotiation_tips.map((tip) => <li key={tip}>{tip}</li>)
              ) : (
                <li>No specific negotiation points detected.</li>
              )}
            </ul>

            <h3>Draft Email</h3>
            <pre>{analysis.draft_email}</pre>
          </article>
        </section>
      )}
    </main>
  );
}
