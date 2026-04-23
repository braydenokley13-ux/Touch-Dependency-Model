"use client";

import { Activity, CheckCircle2, BarChart3, Sparkles } from "lucide-react";

export function EmptyState({ busy }: { busy: boolean }) {
  return (
    <div className="glass-strong relative h-full overflow-hidden rounded-3xl p-8 shadow-card">
      <div className="pointer-events-none absolute -top-24 right-0 h-64 w-64 rounded-full bg-flame-500/15 blur-3xl" />
      <div className="pointer-events-none absolute -bottom-20 left-0 h-56 w-56 rounded-full bg-amber-500/10 blur-3xl" />

      <div className="section-label">Report</div>
      <h3 className="mt-2 font-display text-3xl font-semibold tracking-tight">
        Awaiting evaluation
      </h3>
      <p className="mt-3 max-w-md text-white/60">
        Fill out a stat line or pick a preset. When you hit Run, you&apos;ll get a TDS score,
        archetype fit, scouting summary, and deployment guidance.
      </p>

      <div className="mt-10 grid gap-4 sm:grid-cols-2">
        <Card icon={<Activity className="h-4 w-4" />} title="TDS Score">
          A 0&ndash;100 measure of how efficiency scales across roles.
        </Card>
        <Card icon={<Sparkles className="h-4 w-4" />} title="Archetype">
          One of 12 offensive archetypes with matching role fit.
        </Card>
        <Card icon={<BarChart3 className="h-4 w-4" />} title="Actual vs Expected">
          Side-by-side TS% comparison with residual and z-score.
        </Card>
        <Card icon={<CheckCircle2 className="h-4 w-4" />} title="Strengths &amp; Concerns">
          Ranked signal and risk flags generated from the profile.
        </Card>
      </div>

      {busy ? (
        <div className="mt-10 flex items-center gap-3 text-sm text-white/60">
          <div className="h-1.5 w-full overflow-hidden rounded bg-white/5">
            <div className="shimmer h-full w-1/3" />
          </div>
          <span>Scoring...</span>
        </div>
      ) : null}
    </div>
  );
}

function Card({
  icon,
  title,
  children,
}: {
  icon: React.ReactNode;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="glass rounded-2xl p-4">
      <div className="mb-1 flex items-center gap-2 text-sm font-medium text-white/85">
        <span className="text-flame-400">{icon}</span>
        {title}
      </div>
      <p className="text-sm text-white/55">{children}</p>
    </div>
  );
}
