"use client";

import { useMemo, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Loader2, RotateCcw, Zap } from "lucide-react";
import { evaluatePlayer } from "@/lib/tdm";
import type { PlayerStats, EvaluationReport } from "@/lib/types";
import { PRESETS } from "@/lib/presets";
import { PlayerForm } from "./PlayerForm";
import { ResultsPanel } from "./ResultsPanel";
import { EmptyState } from "./EmptyState";

const defaultStats: PlayerStats = {
  name: "Prospect",
  fg: 180,
  fga: 410,
  ft: 55,
  fta: 65,
  threeP: 120,
  threePA: 290,
  ast: 95,
  tov: 60,
  pts: 535,
  mp: 1950,
  age: 24,
  position: "SF",
};

export function Workbench() {
  const [stats, setStats] = useState<PlayerStats>(defaultStats);
  const [report, setReport] = useState<EvaluationReport | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const runEvaluation = (overrideStats?: PlayerStats) => {
    setError(null);
    setBusy(true);
    try {
      const input = overrideStats ?? stats;
      // Fake a short delay so the UI feels intentional.
      setTimeout(() => {
        try {
          const result = evaluatePlayer(input);
          setReport(result);
        } catch (e: any) {
          setError(e?.message ?? "Evaluation failed");
        } finally {
          setBusy(false);
        }
      }, 280);
    } catch (e: any) {
      setError(e?.message ?? "Evaluation failed");
      setBusy(false);
    }
  };

  const handlePreset = (i: number) => {
    const p = PRESETS[i];
    const s: PlayerStats = { ...p };
    setStats(s);
    runEvaluation(s);
  };

  const reset = () => {
    setReport(null);
    setError(null);
    setStats(defaultStats);
  };

  const presetBlock = useMemo(
    () => (
      <div className="flex flex-wrap gap-2">
        {PRESETS.map((p, i) => (
          <button
            key={p.label}
            onClick={() => handlePreset(i)}
            className="group rounded-full border border-white/10 bg-white/[0.03] px-3 py-1.5 text-xs text-white/70 transition hover:border-flame-500/40 hover:bg-flame-500/10 hover:text-flame-200"
          >
            <span className="mr-1 text-flame-400/70 group-hover:text-flame-300">↳</span>
            {p.label}
          </button>
        ))}
      </div>
    ),
    []
  );

  return (
    <section id="evaluate" className="relative mt-28 scroll-mt-16">
      <div className="mb-8 flex items-end justify-between">
        <div>
          <div className="section-label mb-2">01 — Workbench</div>
          <h2 className="font-display text-3xl font-semibold tracking-tight sm:text-4xl">
            Build a prospect profile
          </h2>
          <p className="mt-3 max-w-2xl text-white/60">
            Enter a season stat line, pick a preset to start, or load a historical player below.
            Everything runs locally in your browser — no data leaves this page.
          </p>
        </div>
      </div>

      <div className="grid gap-8 lg:grid-cols-[minmax(0,1.05fr)_minmax(0,1.4fr)]">
        <motion.div
          layout
          className="glass rounded-3xl p-6 shadow-card sm:p-8"
        >
          <div className="mb-5 flex items-center justify-between">
            <div className="text-sm font-medium text-white/80">Prospect stat sheet</div>
            <button
              onClick={reset}
              className="inline-flex items-center gap-1.5 text-xs text-white/50 hover:text-white"
            >
              <RotateCcw className="h-3 w-3" />
              Reset
            </button>
          </div>
          <div className="mb-4">
            <div className="section-label mb-2">Quick presets</div>
            {presetBlock}
          </div>
          <div className="divider my-6" />
          <PlayerForm stats={stats} onChange={setStats} />

          <button
            onClick={() => runEvaluation()}
            disabled={busy}
            className="group relative mt-8 flex w-full items-center justify-center gap-2 overflow-hidden rounded-2xl bg-gradient-to-b from-flame-400 to-flame-600 py-4 font-medium text-white shadow-glow transition hover:from-flame-400 hover:to-flame-500 disabled:opacity-70"
          >
            <span className="absolute inset-0 -translate-x-full transition group-hover:translate-x-0 bg-gradient-to-r from-transparent via-white/20 to-transparent" />
            {busy ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Scoring...
              </>
            ) : (
              <>
                <Zap className="h-4 w-4" />
                Run TDM Evaluation
              </>
            )}
          </button>
          {error ? (
            <div className="mt-3 rounded-xl border border-red-500/30 bg-red-500/10 px-4 py-3 text-sm text-red-200">
              {error}
            </div>
          ) : null}
        </motion.div>

        <div className="min-h-[620px]">
          <AnimatePresence mode="wait">
            {report ? (
              <motion.div
                key="report"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -16 }}
                transition={{ duration: 0.4, ease: [0.21, 0.47, 0.32, 0.98] }}
              >
                <ResultsPanel report={report} />
              </motion.div>
            ) : (
              <motion.div
                key="empty"
                initial={{ opacity: 0, y: 16 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -16 }}
                transition={{ duration: 0.4 }}
              >
                <EmptyState busy={busy} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
}
