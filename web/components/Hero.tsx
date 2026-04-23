"use client";

import { motion } from "framer-motion";
import { ArrowRight, Sparkles, Target } from "lucide-react";

export function Hero() {
  return (
    <section className="relative pt-12 sm:pt-20">
      <nav className="mb-20 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="relative h-8 w-8">
            <div className="absolute inset-0 rounded-lg bg-gradient-to-br from-flame-400 via-flame-500 to-flame-700 shadow-glow" />
            <div className="absolute inset-[2px] rounded-[7px] bg-ink-950/70 flex items-center justify-center">
              <span className="font-display font-bold text-sm text-flame-400">T</span>
            </div>
          </div>
          <div className="flex flex-col leading-none">
            <span className="font-display text-sm font-semibold tracking-tight">
              Touch Dependency Model
            </span>
            <span className="text-[11px] uppercase tracking-[0.18em] text-ink-600/90 text-white/40">
              Scouting Intelligence
            </span>
          </div>
        </div>
        <div className="hidden items-center gap-6 sm:flex">
          <a href="#evaluate" className="text-sm text-white/70 hover:text-white transition">
            Evaluate
          </a>
          <a href="#methodology" className="text-sm text-white/70 hover:text-white transition">
            Methodology
          </a>
          <a
            href="https://github.com/braydenokley13-ux/touch-dependency-model"
            target="_blank"
            rel="noreferrer"
            className="text-sm text-white/70 hover:text-white transition"
          >
            GitHub
          </a>
        </div>
      </nav>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: [0.21, 0.47, 0.32, 0.98] }}
        className="relative z-10 max-w-4xl"
      >
        <div className="chip mb-6">
          <Sparkles className="h-3.5 w-3.5" />
          Built for recruiting &amp; roster decisions
        </div>
        <h1 className="font-display text-5xl font-bold leading-[1.05] tracking-tight sm:text-7xl">
          Know who{" "}
          <span className="num-gradient">scales</span>
          <br />
          before you sign them.
        </h1>
        <p className="mt-6 max-w-2xl text-lg text-white/70 sm:text-xl">
          TDM measures how a player&apos;s efficiency holds up across roles — from featured scorer
          to off-ball complement — and translates raw box-score stats into a scouting-grade report
          in under a second.
        </p>
        <div className="mt-10 flex flex-wrap gap-3">
          <a
            href="#evaluate"
            className="group inline-flex items-center gap-2 rounded-full bg-white px-5 py-3 text-sm font-medium text-ink-950 transition hover:bg-white/90"
          >
            Evaluate a prospect
            <ArrowRight className="h-4 w-4 transition group-hover:translate-x-0.5" />
          </a>
          <a
            href="#methodology"
            className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-5 py-3 text-sm font-medium text-white/80 transition hover:border-white/30 hover:bg-white/10"
          >
            <Target className="h-4 w-4" />
            How it works
          </a>
        </div>

        <div className="mt-14 grid max-w-3xl grid-cols-3 gap-6 border-t border-white/5 pt-8">
          <Stat label="Archetypes" value="12" />
          <Stat label="Baseline RMSE" value="2.5%" sub="TS% points" />
          <Stat label="Runtime" value="< 30ms" sub="fully client-side" />
        </div>
      </motion.div>
    </section>
  );
}

function Stat({ label, value, sub }: { label: string; value: string; sub?: string }) {
  return (
    <div>
      <div className="section-label">{label}</div>
      <div className="mt-1 flex items-baseline gap-2 font-display">
        <span className="text-2xl font-semibold sm:text-3xl">{value}</span>
        {sub ? <span className="text-xs text-white/50">{sub}</span> : null}
      </div>
    </div>
  );
}
