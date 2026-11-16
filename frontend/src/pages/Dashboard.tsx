import { Link } from "react-router-dom";

function Dashboard() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <header className="border-b border-slate-800 bg-slate-950/80">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <div>
            <h1 className="text-xl font-bold tracking-tight">
              🛡️ PhishGuard
            </h1>
            <p className="text-xs text-slate-400">
              Phishing Detection & Threat Analysis
            </p>
          </div>

          <Link
            to="/email-analyzer"
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium transition hover:bg-blue-500"
          >
            Analyze Email
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-10">
        <div className="mb-10">
          <h2 className="text-3xl font-bold">
            Security Dashboard
          </h2>

          <p className="mt-2 text-slate-400">
            Monitor phishing threats and analyze suspicious emails.
          </p>
        </div>

        <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">
          <StatCard
            title="Emails Scanned"
            value="0"
            description="Total analyzed"
          />

          <StatCard
            title="Phishing Detected"
            value="0"
            description="High-risk emails"
          />

          <StatCard
            title="Suspicious"
            value="0"
            description="Needs investigation"
          />

          <StatCard
            title="Safe"
            value="0"
            description="No major threats"
          />
        </div>

        <div className="mt-8 grid gap-6 lg:grid-cols-2">
          <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
            <h3 className="text-lg font-semibold">
              Email Threat Detection
            </h3>

            <p className="mt-2 text-sm text-slate-400">
              Analyze email content, sender information, URLs,
              authentication results and other phishing indicators.
            </p>

            <Link
              to="/email-analyzer"
              className="mt-6 inline-block rounded-lg bg-blue-600 px-5 py-2.5 text-sm font-medium hover:bg-blue-500"
            >
              Open Email Analyzer →
            </Link>
          </div>

          <div className="rounded-xl border border-slate-800 bg-slate-900 p-6">
            <h3 className="text-lg font-semibold">
              Threat Intelligence
            </h3>

            <p className="mt-2 text-sm text-slate-400">
              URL reputation, suspicious domains and threat indicators
              will appear here in a later phase.
            </p>

            <div className="mt-6 rounded-lg border border-dashed border-slate-700 p-4 text-sm text-slate-500">
              Coming in Phase 2
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

interface StatCardProps {
  title: string;
  value: string;
  description: string;
}

function StatCard({
  title,
  value,
  description,
}: StatCardProps) {
  return (
    <div className="rounded-xl border border-slate-800 bg-slate-900 p-5">
      <p className="text-sm text-slate-400">{title}</p>

      <p className="mt-2 text-3xl font-bold">
        {value}
      </p>

      <p className="mt-1 text-xs text-slate-500">
        {description}
      </p>
    </div>
  );
}

export default Dashboard;