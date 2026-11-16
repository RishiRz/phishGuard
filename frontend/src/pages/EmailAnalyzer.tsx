import { useState } from "react";
import axios from "axios";

interface UrlResult {
  url: string;
  hostname: string;
  domain: string;
  risk_score: number;
  risk_level: string;
  reasons: string[];
}

interface MlAnalysis {
  prediction: string;
  confidence: number;
  spam_probability: number;
  phishing_probability: number;
  malicious_probability: number;
  probabilities: {
    Legitimate: number;
    Spam: number;
    Phishing: number;
  };
}

interface ScoreComponent {
  score: number;
  weight: number;
  contribution: number;
}

interface ScoreBreakdown {
  rules: ScoreComponent;
  urls: ScoreComponent;
  headers: ScoreComponent;
  ml: ScoreComponent;
}

interface AnalysisResult {
  classification: string;
  risk_score: number;
  risk_level: string;
  reasons: string[];
  urls?: UrlResult[];
  ml_analysis?: MlAnalysis;
  score_breakdown?: ScoreBreakdown;
}

interface AuthenticationMethod {
  status: string;
  evidence: string[];
}

interface HeaderAnalysis {
  authentication: {
    spf: AuthenticationMethod;
    dkim: AuthenticationMethod;
    dmarc: AuthenticationMethod;
  };
  warnings: string[];
  issues?: {
    reply_to_mismatch: boolean;
    return_path_mismatch: boolean;
  };
}

const SCORE_COMPONENTS: {
  key: keyof ScoreBreakdown;
  label: string;
}[] = [
  { key: "rules", label: "Rule Analysis" },
  { key: "urls", label: "URL Analysis" },
  { key: "headers", label: "Header Analysis" },
  { key: "ml", label: "ML Prediction" },
];

function EmailAnalyzer() {
  const [sender, setSender] = useState("");
  const [subject, setSubject] = useState("");
  const [body, setBody] = useState("");

  const [selectedFile, setSelectedFile] =
    useState<File | null>(null);

  const [analysisMode, setAnalysisMode] =
  useState<"text" | "eml">("text");

  const [loading, setLoading] = useState(false);

  const [result, setResult] =
    useState<AnalysisResult | null>(null);

  const [headerAnalysis, setHeaderAnalysis] =
    useState<HeaderAnalysis | null>(null);

  // ==========================================
  // Analyze pasted email
  // ==========================================

  const analyzeEmail = async () => {
    if (!body.trim()) {
      alert("Please enter the email body.");
      return;
    }

    try {
      setLoading(true);
      setResult(null);
      setHeaderAnalysis(null);

      const response = await axios.post(
        "http://localhost:8000/api/analyze",
        {
          sender,
          subject,
          body,
        }
      );

      setResult(response.data);
    } catch (error) {
      console.error(error);

      alert(
        "Unable to connect to the backend."
      );
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // Analyze .eml file
  // ==========================================

  const analyzeEml = async () => {
    if (!selectedFile) {
      alert("Please select an .eml file.");
      return;
    }

    try {
      setLoading(true);
      setResult(null);
      setHeaderAnalysis(null);

      const formData = new FormData();

      formData.append(
        "file",
        selectedFile
      );

      const response = await axios.post(
        "http://localhost:8000/api/analyze-eml",
        formData,
        {
          headers: {
            "Content-Type":
              "multipart/form-data",
          },
        }
      );

      setResult(response.data.analysis);

      setHeaderAnalysis(
        response.data.headers
      );
    } catch (error) {
      console.error(error);

      alert(
        "Unable to analyze the .eml file."
      );
    } finally {
      setLoading(false);
    }
  };

  // ==========================================
  // Main UI
  // ==========================================

  return (
    <div className="min-h-screen bg-slate-950 text-white">

      {/* Header */}

      <header className="border-b border-slate-800">
        <div className="mx-auto max-w-6xl px-6 py-5">

          <h1 className="text-xl font-bold">
            🛡️ PhishGuard
          </h1>

          <p className="text-xs text-slate-500">
            Phishing Detection & Threat Analysis
          </p>

        </div>
      </header>

      {/* Main */}

      <main className="mx-auto max-w-6xl px-6 py-10">

        <div className="mb-8">

          <h2 className="text-3xl font-bold">
            Email Analyzer
          </h2>

          <p className="mt-2 text-slate-400">
            Analyze an email for potential
            phishing indicators.
          </p>

        </div>

        <div className="grid gap-8 lg:grid-cols-2">

          {/* ================================= */}
          {/* LEFT SIDE */}
          {/* ================================= */}

          <section className="rounded-xl border border-slate-800 bg-slate-900 p-6">

            <h3 className="mb-6 text-lg font-semibold">
              Email Information
            </h3>

            {/* Mode selector */}

            <div className="mb-6 flex rounded-lg bg-slate-950 p-1">

              <button
                onClick={() => {
                  setAnalysisMode("text");
                  setResult(null);
                  setHeaderAnalysis(null);
                }}
                className={`flex-1 rounded-md px-4 py-2 text-sm ${
                  analysisMode === "text"
                    ? "bg-blue-600 text-white"
                    : "text-slate-400"
                }`}
              >
                Paste Email
              </button>

              <button
                onClick={() => {
                  setAnalysisMode("eml");
                  setResult(null);
                  setHeaderAnalysis(null);
                }}
                className={`flex-1 rounded-md px-4 py-2 text-sm ${
                  analysisMode === "eml"
                    ? "bg-blue-600 text-white"
                    : "text-slate-400"
                }`}
              >
                Upload .eml
              </button>

            </div>

            {/* ================================= */}
            {/* TEXT MODE */}
            {/* ================================= */}

            {analysisMode === "text" && (

              <div className="space-y-5">

                {/* Sender */}

                <div>

                  <label className="mb-2 block text-sm text-slate-300">
                    Sender
                  </label>

                  <input
                    type="email"
                    value={sender}
                    onChange={(e) =>
                      setSender(e.target.value)
                    }
                    placeholder="security@example.com"
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm outline-none focus:border-blue-500"
                  />

                </div>

                {/* Subject */}

                <div>

                  <label className="mb-2 block text-sm text-slate-300">
                    Subject
                  </label>

                  <input
                    type="text"
                    value={subject}
                    onChange={(e) =>
                      setSubject(e.target.value)
                    }
                    placeholder="Your account requires verification"
                    className="w-full rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm outline-none focus:border-blue-500"
                  />

                </div>

                {/* Body */}

                <div>

                  <label className="mb-2 block text-sm text-slate-300">
                    Email Body
                  </label>

                  <textarea
                    value={body}
                    onChange={(e) =>
                      setBody(e.target.value)
                    }
                    placeholder="Paste the email content here..."
                    rows={12}
                    className="w-full resize-none rounded-lg border border-slate-700 bg-slate-950 px-4 py-3 text-sm outline-none focus:border-blue-500"
                  />

                </div>

                {/* Analyze */}

                <button
                  onClick={analyzeEmail}
                  disabled={loading}
                  className="w-full rounded-lg bg-blue-600 px-5 py-3 font-medium transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {loading
                    ? "Analyzing..."
                    : "Analyze Email"}
                </button>

              </div>

            )}

            {/* ================================= */}
            {/* EML MODE */}
            {/* ================================= */}

            {analysisMode === "eml" && (

              <div className="space-y-5">

                <div className="rounded-xl border border-dashed border-slate-700 bg-slate-950 p-8 text-center">

                  <div className="text-4xl">
                    📧
                  </div>

                  <h4 className="mt-4 font-semibold">
                    Upload Email File
                  </h4>

                  <p className="mt-2 text-sm text-slate-500">
                    Upload an .eml file for
                    header, URL and phishing
                    analysis.
                  </p>

                  <input
                    type="file"
                    accept=".eml,message/rfc822"
                    onChange={(e) => {

                      const file =
                        e.target.files?.[0] ?? null;

                      setSelectedFile(file);

                    }}
                    className="mt-6 block w-full text-sm text-slate-400"
                  />

                  {selectedFile && (

                    <p className="mt-4 text-sm text-blue-400">
                      Selected:{" "}
                      {selectedFile.name}
                    </p>

                  )}

                </div>

                <button
                  onClick={analyzeEml}
                  disabled={
                    loading ||
                    !selectedFile
                  }
                  className="w-full rounded-lg bg-blue-600 px-5 py-3 font-medium transition hover:bg-blue-500 disabled:cursor-not-allowed disabled:opacity-50"
                >
                  {loading
                    ? "Analyzing..."
                    : "Analyze .eml"}
                </button>

              </div>

            )}

          </section>

          {/* ================================= */}
          {/* RIGHT SIDE */}
          {/* ================================= */}

          <section className="rounded-xl border border-slate-800 bg-slate-900 p-6">

            <h3 className="mb-6 text-lg font-semibold">
              Analysis Result
            </h3>

            {/* No result */}

            {!result && (

              <div className="flex min-h-[400px] items-center justify-center rounded-lg border border-dashed border-slate-700">

                <div className="text-center">

                  <div className="text-4xl">
                    🔍
                  </div>

                  <p className="mt-4 text-slate-400">
                    Submit an email to begin
                    analysis.
                  </p>

                </div>

              </div>

            )}

            {/* Result */}

            {result && (

              <div className="space-y-6">

                {/* Risk Score */}

                <div className="rounded-lg border border-slate-700 bg-slate-950 p-6 text-center">

                  <p className="text-sm text-slate-400">
                    Risk Score
                  </p>

                  <p className="mt-2 text-5xl font-bold">

                    {result.risk_score}

                    <span className="text-xl text-slate-500">
                      /100
                    </span>

                  </p>

                  <p className="mt-3 text-lg font-semibold">
                    {result.risk_level}
                  </p>

                </div>

                {/* Risk Score Breakdown */}

                {result.score_breakdown && (

                  <div>

                    <h4 className="mb-3 font-semibold">
                      Risk Score Breakdown
                    </h4>

                    <div className="space-y-3">

                      {SCORE_COMPONENTS.map(
                        ({ key, label }) => {

                          const part =
                            result.score_breakdown![key];

                          return (

                            <div
                              key={key}
                              className="rounded-lg border border-slate-800 bg-slate-950 p-3"
                            >

                              <div className="flex items-center justify-between text-sm">

                                <span className="text-slate-300">
                                  {label}
                                </span>

                                <span className="text-slate-400">
                                  {part.contribution}
                                  {" / "}
                                  {part.weight}
                                </span>

                              </div>

                              <div className="mt-2 h-2 w-full overflow-hidden rounded-full bg-slate-800">

                                <div
                                  className="h-full rounded-full bg-blue-500"
                                  style={{
                                    width: `${part.score}%`,
                                  }}
                                />

                              </div>

                              <p className="mt-2 text-xs text-slate-500">
                                Component score:{" "}
                                {part.score}/100
                                {" · "}
                                Weight: {part.weight}%
                              </p>

                            </div>

                          );

                        }
                      )}

                    </div>

                  </div>

                )}

                {/* Classification */}

                <div>

                  <h4 className="mb-3 font-semibold">
                    Classification
                  </h4>

                  <div className="rounded-lg bg-slate-950 p-4">
                    {result.classification}
                  </div>

                </div>

                {/* ML Analysis */}

                {/* ML Analysis */}

                {result.ml_analysis && (

                  <div>

                    <h4 className="mb-3 font-semibold">
                      Machine Learning Analysis
                    </h4>

                    {/* Prediction Summary */}

                    <div className="mb-4 rounded-lg border border-slate-800 bg-slate-950 p-4">

                      <div className="flex items-center justify-between">

                        <div>
                          <p className="text-xs uppercase text-slate-500">
                            Model Prediction
                          </p>

                          <p className="mt-2 text-2xl font-bold">
                            {result.ml_analysis.prediction}
                          </p>
                        </div>

                        <div className="text-right">
                          <p className="text-xs uppercase text-slate-500">
                            Confidence
                          </p>

                          <p className="mt-2 text-2xl font-bold text-blue-400">
                            {result.ml_analysis.confidence}%
                          </p>
                        </div>

                      </div>

                    </div>

                    {/* Class Probabilities */}

                    <div className="space-y-4">

                      <p className="text-sm font-medium text-slate-300">
                        Classification Probabilities
                      </p>

                      {(
                        [
                          {
                            label: "Legitimate",
                            value: result.ml_analysis.probabilities.Legitimate,
                            color: "bg-emerald-500",
                          },
                          {
                            label: "Spam",
                            value: result.ml_analysis.probabilities.Spam,
                            color: "bg-yellow-500",
                          },
                          {
                            label: "Phishing",
                            value: result.ml_analysis.probabilities.Phishing,
                            color: "bg-red-500",
                          },
                        ]
                      ).map((item) => (

                        <div key={item.label}>

                          <div className="mb-2 flex justify-between text-sm">

                            <span className="text-slate-300">
                              {item.label}
                            </span>

                            <span className="font-semibold text-white">
                              {item.value}%
                            </span>

                          </div>

                          <div className="h-3 w-full overflow-hidden rounded-full bg-slate-800">

                            <div
                              className={`h-full rounded-full ${item.color}`}
                              style={{
                                width: `${Math.min(
                                  100,
                                  Math.max(0, item.value)
                                )}%`,
                              }}
                            />

                          </div>

                        </div>

                      ))}

                    </div>

                    {/* Malicious Probability */}

                    <div className="mt-5 grid gap-3 sm:grid-cols-2">

                      <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">

                        <p className="text-xs uppercase text-slate-500">
                          Malicious Probability
                        </p>

                        <p className="mt-2 text-xl font-bold text-red-400">
                          {result.ml_analysis.malicious_probability}%
                        </p>

                        <p className="mt-1 text-xs text-slate-500">
                          Combined Spam + Phishing probability
                        </p>

                      </div>

                      <div className="rounded-lg border border-slate-800 bg-slate-950 p-4">

                        <p className="text-xs uppercase text-slate-500">
                          Phishing Probability
                        </p>

                        <p className="mt-2 text-xl font-bold text-orange-400">
                          {result.ml_analysis.phishing_probability}%
                        </p>

                        <p className="mt-1 text-xs text-slate-500">
                          Probability assigned to phishing
                        </p>

                      </div>

                    </div>

                  </div>

                )}

                {/* Detection Reasons */}

                <div>

                  <h4 className="mb-3 font-semibold">
                    Detection Reasons
                  </h4>

                  <div className="space-y-2">

                    {result.reasons.map(
                      (reason, index) => (

                        <div
                          key={index}
                          className="rounded-lg border border-slate-800 bg-slate-950 p-3 text-sm text-slate-300"
                        >
                          ⚠️ {reason}
                        </div>

                      )
                    )}

                  </div>

                </div>

                {/* URL Analysis */}

                {result.urls &&
                  result.urls.length > 0 && (

                    <div>

                      <h4 className="mb-3 font-semibold">
                        Detected URLs
                      </h4>

                      <div className="space-y-3">

                        {result.urls.map(
                          (url) => (

                            <div
                              key={url.url}
                              className="rounded-lg border border-slate-800 bg-slate-950 p-4"
                            >

                              <div className="break-all text-sm text-blue-400">
                                {url.url}
                              </div>

                              <div className="mt-2 flex items-center justify-between">

                                <span className="text-xs text-slate-500">
                                  {url.domain ||
                                    url.hostname}
                                </span>

                                <span className="text-xs font-semibold">
                                  {url.risk_level}
                                  {" "}
                                  ({url.risk_score}/100)
                                </span>

                              </div>

                              {url.reasons.length >
                                0 && (

                                <div className="mt-3 space-y-1">

                                  {url.reasons.map(
                                    (
                                      reason,
                                      index
                                    ) => (

                                      <p
                                        key={
                                          index
                                        }
                                        className="text-xs text-slate-400"
                                      >
                                        •{" "}
                                        {reason}
                                      </p>

                                    )
                                  )}

                                </div>

                              )}

                            </div>

                          )
                        )}

                      </div>

                    </div>

                  )}

                {/* SPF / DKIM / DMARC */}

                {headerAnalysis && (

                  <div>

                    <h4 className="mb-3 font-semibold">
                      Email Authentication
                    </h4>

                    <div className="grid gap-3 md:grid-cols-3">

                      {[
                        "spf",
                        "dkim",
                        "dmarc",
                      ].map((method) => {

                        const auth =
                          headerAnalysis
                            .authentication[
                              method as
                                | "spf"
                                | "dkim"
                                | "dmarc"
                            ];

                        return (

                          <div
                            key={method}
                            className="rounded-lg border border-slate-800 bg-slate-950 p-4"
                          >

                            <p className="text-xs uppercase text-slate-500">
                              {method}
                            </p>

                            <p className="mt-2 text-lg font-bold">
                              {auth.status}
                            </p>

                            {auth.evidence.map(
                              (
                                evidence,
                                index
                              ) => (

                                <p
                                  key={
                                    index
                                  }
                                  className="mt-2 text-xs text-slate-500"
                                >
                                  {evidence}
                                </p>

                              )
                            )}

                          </div>

                        );

                      })}

                    </div>

                    {/* Header warnings */}

                    {headerAnalysis
                      .warnings
                      .length > 0 && (

                      <div className="mt-4 space-y-2">

                        {headerAnalysis.warnings.map(
                          (
                            warning,
                            index
                          ) => (

                            <div
                              key={index}
                              className="rounded-lg border border-yellow-900/50 bg-yellow-950/20 p-3 text-sm text-yellow-400"
                            >
                              ⚠️ {warning}
                            </div>

                          )
                        )}

                      </div>

                    )}

                  </div>

                )}

              </div>

            )}

          </section>

        </div>

      </main>

    </div>
  );
}

export default EmailAnalyzer;

