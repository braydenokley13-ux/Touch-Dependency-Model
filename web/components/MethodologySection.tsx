"use client";

import { motion } from "framer-motion";
import {
  Gauge,
  GitBranch,
  Workflow,
  ShieldCheck,
} from "lucide-react";

const STEPS = [
  {
    icon: <Gauge className="h-4 w-4" />,
    title: "Feature engineering",
    body:
      "Turn box-score inputs into usage rate, assist rate, shot diet (3PA/FTA), per-36 volume, and pace-adjusted efficiency.",
  },
  {
    icon: <Workflow className="h-4 w-4" />,
    title: "Efficiency model",
    body:
      "A regression surface predicts expected True Shooting % given the player's touch load and shot selection profile.",
  },
  {
    icon: <GitBranch className="h-4 w-4" />,
    title: "Residual → TDS",
    body:
      "The gap between actual and expected TS% is converted to a 0–100 percentile. High TDS = efficiency that holds across roles.",
  },
  {
    icon: <ShieldCheck className="h-4 w-4" />,
    title: "Archetype fit",
    body:
      "The profile is matched to one of twelve offensive archetypes to contextualize role, ecosystem fit, and development path.",
  },
];

export function MethodologySection() {
  return (
    <section id="methodology" className="relative mt-32 scroll-mt-16">
      <div className="mb-10">
        <div className="section-label mb-2">02 — How TDM works</div>
        <h2 className="font-display text-3xl font-semibold tracking-tight sm:text-4xl">
          From stat line to scouting report in four steps.
        </h2>
        <p className="mt-3 max-w-2xl text-white/60">
          TDM isn&apos;t a black box. Every score comes from a deterministic pipeline you can
          inspect &mdash; no surprises, no drift, same inputs always produce the same outputs.
        </p>
      </div>
      <div className="grid gap-5 md:grid-cols-2 lg:grid-cols-4">
        {STEPS.map((s, i) => (
          <motion.div
            key={s.title}
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-80px" }}
            transition={{ delay: i * 0.08, duration: 0.5 }}
            className="glass relative overflow-hidden rounded-2xl p-5"
          >
            <div className="absolute right-4 top-4 font-display text-2xl font-semibold text-white/5">
              0{i + 1}
            </div>
            <div className="mb-3 inline-flex h-8 w-8 items-center justify-center rounded-lg border border-flame-500/30 bg-flame-500/10 text-flame-300">
              {s.icon}
            </div>
            <h3 className="text-[15px] font-semibold text-white/90">{s.title}</h3>
            <p className="mt-1.5 text-sm text-white/55">{s.body}</p>
          </motion.div>
        ))}
      </div>

      <div className="mt-10 grid gap-5 md:grid-cols-3">
        <TDSBand range="80-100" label="Highly Scalable" body="Plug-and-play in any system." tone="emerald" />
        <TDSBand range="50-70" label="Neutral → Scalable" body="Adapts to varied roles." tone="blue" />
        <TDSBand range="0-40" label="Touch Dependent" body="Needs specific role to produce." tone="flame" />
      </div>
    </section>
  );
}

function TDSBand({
  range,
  label,
  body,
  tone,
}: {
  range: string;
  label: string;
  body: string;
  tone: "emerald" | "blue" | "flame";
}) {
  const color =
    tone === "emerald"
      ? "from-emerald-400/15 to-emerald-400/0 border-emerald-400/20"
      : tone === "blue"
      ? "from-sky-400/15 to-sky-400/0 border-sky-400/20"
      : "from-flame-500/15 to-flame-500/0 border-flame-500/20";
  const pill =
    tone === "emerald"
      ? "text-emerald-300 bg-emerald-400/10 border-emerald-400/30"
      : tone === "blue"
      ? "text-sky-300 bg-sky-400/10 border-sky-400/30"
      : "text-flame-300 bg-flame-500/10 border-flame-500/30";
  return (
    <div className={`relative overflow-hidden rounded-2xl border bg-gradient-to-br p-5 ${color}`}>
      <div className={`inline-block rounded-full border px-2.5 py-0.5 text-[11px] ${pill}`}>{range}</div>
      <div className="mt-3 font-display text-xl font-semibold">{label}</div>
      <div className="mt-1 text-sm text-white/60">{body}</div>
    </div>
  );
}
