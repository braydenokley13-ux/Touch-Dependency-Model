"use client";

import { motion } from "framer-motion";

interface Props {
  actual: number; // 0-1
  expected: number; // 0-1
}

export function EfficiencyComparison({ actual, expected }: Props) {
  const min = 0.4;
  const max = 0.7;
  const scale = (v: number) => ((Math.max(min, Math.min(max, v)) - min) / (max - min)) * 100;
  const actualPct = scale(actual);
  const expectedPct = scale(expected);
  const diff = actual - expected;
  const over = diff >= 0;

  return (
    <div className="mt-6 space-y-5">
      <Row
        label="Actual TS%"
        value={`${(actual * 100).toFixed(1)}%`}
        pct={actualPct}
        color={over ? "emerald" : "flame"}
        accent
      />
      <Row
        label="Expected TS%"
        value={`${(expected * 100).toFixed(1)}%`}
        pct={expectedPct}
        color="neutral"
      />
      <div className="pt-2">
        <div className="flex items-center justify-between">
          <span className="text-sm text-white/60">Residual</span>
          <span
            className={`font-display text-lg font-semibold ${
              over ? "text-emerald-300" : "text-flame-400"
            }`}
          >
            {over ? "+" : ""}
            {(diff * 100).toFixed(2)} pts
          </span>
        </div>
        <div className="mt-1 text-xs text-white/45">
          {over
            ? "Beating what the model expects from a profile like this."
            : "Coming in under expected efficiency for this profile."}
        </div>
      </div>

      <TickScale min={min} max={max} />
    </div>
  );
}

function Row({
  label,
  value,
  pct,
  color,
  accent,
}: {
  label: string;
  value: string;
  pct: number;
  color: "emerald" | "flame" | "neutral";
  accent?: boolean;
}) {
  const gradient =
    color === "emerald"
      ? "from-emerald-400 to-emerald-600"
      : color === "flame"
      ? "from-flame-400 to-flame-600"
      : "from-white/40 to-white/10";
  return (
    <div>
      <div className="mb-1.5 flex items-baseline justify-between">
        <span className="text-sm text-white/70">{label}</span>
        <span
          className={`font-display text-base font-semibold ${
            accent ? "num-gradient" : "text-white/85"
          }`}
        >
          {value}
        </span>
      </div>
      <div className="h-2 overflow-hidden rounded-full bg-white/5">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.9, ease: [0.21, 0.47, 0.32, 0.98] }}
          className={`h-full rounded-full bg-gradient-to-r ${gradient}`}
        />
      </div>
    </div>
  );
}

function TickScale({ min, max }: { min: number; max: number }) {
  const ticks = [min, (min + max) / 2, max];
  return (
    <div className="mt-2 flex items-center justify-between text-[11px] uppercase tracking-widest text-white/30">
      {ticks.map((t) => (
        <span key={t}>{(t * 100).toFixed(0)}%</span>
      ))}
    </div>
  );
}
