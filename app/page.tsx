"use client";

import { useState } from "react";
import PlayerForm from "@/components/PlayerForm";
import ResultPanel from "@/components/ResultPanel";
import type { EvaluationReport } from "@/lib/types";

export default function Home() {
  const [report, setReport] = useState<EvaluationReport | null>(null);
  const [error, setError] = useState<string>("");
  const [loading, setLoading] = useState(false);

  return (
    <main className="mx-auto max-w-6xl px-4 py-10 md:py-16">
      <header className="mb-10 text-center">
        <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/[0.04] px-3 py-1 text-xs font-medium uppercase tracking-wider text-court-500">
          <span className="h-1.5 w-1.5 rounded-full bg-court-500" />
          Basketball Analytics
        </div>
        <h1 className="mt-4 text-4xl md:text-5xl font-bold tracking-tight">
          Touch Dependency Model
        </h1>
        <p className="mt-3 max-w-2xl mx-auto text-slate-400">
          Predict how a player&apos;s offensive efficiency scales with role.
          Enter season totals and the trained ensemble returns a TDS score,
          archetype, and scouting outlook.
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        <div className="lg:col-span-3">
          <PlayerForm
            onResult={setReport}
            onError={setError}
            setLoading={setLoading}
            loading={loading}
          />
        </div>
        <div className="lg:col-span-2">
          {error && (
            <div className="card p-5 border border-rose-500/40 bg-rose-500/10 text-sm text-rose-200">
              <div className="font-semibold mb-1">Error</div>
              <div className="whitespace-pre-wrap">{error}</div>
            </div>
          )}
          {!error && !report && !loading && <EmptyState />}
          {loading && <LoadingState />}
          {report && !loading && <ResultPanel report={report} />}
        </div>
      </div>

      <footer className="mt-16 border-t border-white/10 pt-6 text-center text-xs text-slate-500">
        <p>
          Ensemble RMSE ~0.012 TS% · Linear + XGBoost · 12 archetype clusters
        </p>
        <p className="mt-1">
          Built on the Touch Dependency Model package · Deployed on Vercel
        </p>
      </footer>
    </main>
  );
}

function EmptyState() {
  return (
    <div className="card p-8 text-center">
      <div className="mx-auto mb-3 inline-flex h-12 w-12 items-center justify-center rounded-full bg-court-500/15 text-court-500 text-2xl">
        ●
      </div>
      <h3 className="text-base font-semibold">Awaiting input</h3>
      <p className="mt-2 text-sm text-slate-400">
        Fill in the form (or load a preset) and run an evaluation to see the
        TDS score, archetype, and scouting report.
      </p>
    </div>
  );
}

function LoadingState() {
  return (
    <div className="card p-8 text-center">
      <div className="mx-auto h-6 w-6 animate-spin rounded-full border-2 border-court-500 border-t-transparent" />
      <p className="mt-3 text-sm text-slate-400">
        Running ensemble inference…
      </p>
    </div>
  );
}
