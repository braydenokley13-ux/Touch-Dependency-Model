"use client";

import { motion } from "framer-motion";
import {
  BadgeCheck,
  AlertTriangle,
  TrendingUp,
  Target,
  Compass,
  Layers,
  GraduationCap,
  Sparkles,
} from "lucide-react";
import { EvaluationReport } from "@/lib/types";
import { formatPct } from "@/lib/utils";
import { TDSDial } from "./TDSDial";
import { EfficiencyComparison } from "./EfficiencyComparison";
import { RadarFingerprint } from "./RadarFingerprint";

interface Props {
  report: EvaluationReport;
}

export function ResultsPanel({ report }: Props) {
  return (
    <div className="flex flex-col gap-6">
      {/* Header card */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
        className="glass-strong relative overflow-hidden rounded-3xl p-8 shadow-card"
      >
        <div className="pointer-events-none absolute -top-24 right-0 h-60 w-60 rounded-full bg-flame-500/20 blur-3xl" />
        <div className="grid gap-8 md:grid-cols-[auto_1fr]">
          <TDSDial value={report.tdsScore} category={report.tdsCategory} />
          <div className="flex min-w-0 flex-col justify-between gap-4">
            <div>
              <div className="section-label">Evaluation</div>
              <h3 className="mt-1 font-display text-3xl font-semibold tracking-tight">
                {report.playerName}
              </h3>
              <div className="mt-2 flex flex-wrap gap-2">
                <span className="chip">
                  <Sparkles className="h-3 w-3" />
                  {report.archetype}
                </span>
                <span className="chip-muted">
                  {report.tdsCategory}
                </span>
              </div>
              <p className="mt-4 text-white/70">{report.shortSummary}</p>
            </div>

            <div className="grid grid-cols-3 gap-4 border-t border-white/5 pt-4">
              <MiniStat label="Actual TS%" value={formatPct(report.actualTs)} accent />
              <MiniStat label="Expected TS%" value={formatPct(report.predictedTs)} />
              <MiniStat
                label="Residual"
                value={`${report.residual >= 0 ? "+" : ""}${(report.residual * 100).toFixed(1)}%`}
                positive={report.residual >= 0}
              />
            </div>
          </div>
        </div>
      </motion.div>

      {/* Charts row */}
      <div className="grid gap-6 md:grid-cols-2">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="glass rounded-3xl p-6 shadow-card"
        >
          <CardHeader
            icon={<TrendingUp className="h-4 w-4" />}
            title="Actual vs Expected TS%"
            subtitle="Residual drives the TDS percentile"
          />
          <EfficiencyComparison
            actual={report.actualTs}
            expected={report.predictedTs}
          />
        </motion.div>
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="glass rounded-3xl p-6 shadow-card"
        >
          <CardHeader
            icon={<Layers className="h-4 w-4" />}
            title="Profile Fingerprint"
            subtitle="Normalized against league baselines"
          />
          <RadarFingerprint features={report.features} />
        </motion.div>
      </div>

      {/* Scouting summary */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="glass rounded-3xl p-6 shadow-card sm:p-8"
      >
        <CardHeader
          icon={<Compass className="h-4 w-4" />}
          title="Scouting summary"
          subtitle="Narrative read of fit, risk, and ecosystem value"
        />
        <p className="mt-4 text-[15px] leading-relaxed text-white/80">
          {report.scoutingSummary}
        </p>
        <div className="mt-6 grid gap-4 sm:grid-cols-2">
          <ListBlock
            title="Strengths"
            icon={<BadgeCheck className="h-4 w-4 text-emerald-400" />}
            items={report.strengths}
            tone="good"
          />
          <ListBlock
            title="Concerns"
            icon={<AlertTriangle className="h-4 w-4 text-amber-400" />}
            items={report.concerns.length ? report.concerns : ["No major flags identified."]}
            tone="warn"
          />
        </div>
      </motion.div>

      {/* Recommendations */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.25 }}
        className="glass rounded-3xl p-6 shadow-card sm:p-8"
      >
        <CardHeader
          icon={<Target className="h-4 w-4" />}
          title="Front-office guidance"
          subtitle={report.oneLiner}
        />
        <div className="mt-4 grid gap-4 sm:grid-cols-2">
          <Rec
            label="Deployment"
            icon={<Layers className="h-4 w-4" />}
            body={report.recommendations.deployment}
          />
          <Rec
            label="Acquisition"
            icon={<Target className="h-4 w-4" />}
            body={report.recommendations.acquisition}
          />
          <Rec
            label="Market value"
            icon={<TrendingUp className="h-4 w-4" />}
            body={report.recommendations.marketValue}
          />
          <Rec
            label="Development"
            icon={<GraduationCap className="h-4 w-4" />}
            body={report.recommendations.development}
          />
        </div>
      </motion.div>

      {/* Feature Breakdown */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="glass rounded-3xl p-6 shadow-card"
      >
        <CardHeader
          icon={<Sparkles className="h-4 w-4" />}
          title="Feature breakdown"
          subtitle="Computed values that feed the model"
        />
        <div className="mt-4 grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-5">
          <FeatureTile label="USG%" value={report.features.usgPct.toFixed(1)} />
          <FeatureTile label="AST%" value={report.features.astPct.toFixed(1)} />
          <FeatureTile label="TOV%" value={report.features.tovPct.toFixed(1)} />
          <FeatureTile
            label="3PA rate"
            value={`${(report.features.threePARate * 100).toFixed(0)}%`}
          />
          <FeatureTile
            label="FTA rate"
            value={`${(report.features.ftaRate * 100).toFixed(0)}%`}
          />
          <FeatureTile label="PTS / 36" value={report.features.ptsPer36.toFixed(1)} />
          <FeatureTile label="AST / 36" value={report.features.astPer36.toFixed(1)} />
          <FeatureTile label="FGA / 36" value={report.features.fgaPer36.toFixed(1)} />
          <FeatureTile label="FT%" value={formatPct(report.features.ftPct, 0)} />
          <FeatureTile label="Z-Score" value={report.zScore.toFixed(2)} />
        </div>
      </motion.div>
    </div>
  );
}

function CardHeader({
  icon,
  title,
  subtitle,
}: {
  icon: React.ReactNode;
  title: string;
  subtitle?: string;
}) {
  return (
    <div>
      <div className="flex items-center gap-2 text-sm font-medium text-white/85">
        <span className="text-flame-400">{icon}</span>
        {title}
      </div>
      {subtitle ? <div className="mt-1 text-[13px] text-white/50">{subtitle}</div> : null}
    </div>
  );
}

function MiniStat({
  label,
  value,
  accent,
  positive,
}: {
  label: string;
  value: string;
  accent?: boolean;
  positive?: boolean;
}) {
  return (
    <div>
      <div className="text-[11px] uppercase tracking-widest text-white/40">{label}</div>
      <div
        className={`mt-1 font-display text-xl font-semibold ${
          accent ? "num-gradient" : positive === false ? "text-red-300" : positive ? "text-emerald-300" : "text-white"
        }`}
      >
        {value}
      </div>
    </div>
  );
}

function ListBlock({
  title,
  icon,
  items,
  tone,
}: {
  title: string;
  icon: React.ReactNode;
  items: string[];
  tone: "good" | "warn";
}) {
  return (
    <div
      className={`rounded-2xl border p-4 ${
        tone === "good"
          ? "border-emerald-500/15 bg-emerald-500/[0.04]"
          : "border-amber-500/15 bg-amber-500/[0.04]"
      }`}
    >
      <div className="mb-2 flex items-center gap-2 text-sm font-medium text-white/85">
        {icon}
        {title}
      </div>
      <ul className="space-y-1.5 text-sm text-white/70">
        {items.map((it, i) => (
          <li key={i} className="flex gap-2">
            <span className="mt-1 h-1 w-1 flex-none rounded-full bg-white/40" />
            <span>{it}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

function Rec({
  label,
  icon,
  body,
}: {
  label: string;
  icon: React.ReactNode;
  body: string;
}) {
  return (
    <div className="rounded-2xl border border-white/8 bg-white/[0.025] p-4">
      <div className="mb-1.5 flex items-center gap-2 text-sm font-medium text-white/85">
        <span className="text-flame-400">{icon}</span>
        {label}
      </div>
      <p className="text-[13.5px] leading-relaxed text-white/65">{body}</p>
    </div>
  );
}

function FeatureTile({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-white/5 bg-white/[0.02] px-3 py-3">
      <div className="text-[10px] uppercase tracking-widest text-white/45">{label}</div>
      <div className="mt-0.5 font-display text-lg font-semibold">{value}</div>
    </div>
  );
}
