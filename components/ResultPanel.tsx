import type { EvaluationReport } from "@/lib/types";

interface Props {
  report: EvaluationReport;
}

function tdsColor(score: number): string {
  if (score >= 70) return "bg-emerald-500/20 text-emerald-300 border-emerald-400/40";
  if (score >= 55) return "bg-sky-500/20 text-sky-300 border-sky-400/40";
  if (score >= 45) return "bg-amber-500/20 text-amber-300 border-amber-400/40";
  if (score >= 35) return "bg-orange-500/20 text-orange-300 border-orange-400/40";
  return "bg-rose-500/20 text-rose-300 border-rose-400/40";
}

function pct(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export default function ResultPanel({ report }: Props) {
  const tdsClass = tdsColor(report.tds_score);
  const residualPct = report.residual * 100;

  return (
    <div className="space-y-5">
      <div className={`card p-6 border ${tdsClass}`}>
        <div className="flex items-start justify-between gap-4 flex-wrap">
          <div>
            <div className="label">Touch Dependency Score</div>
            <div className="mt-2 flex items-baseline gap-3">
              <span className="text-6xl font-bold tracking-tight">
                {report.tds_score.toFixed(1)}
              </span>
              <span className="text-sm font-medium opacity-80">
                {report.tds_category}
              </span>
            </div>
            <p className="mt-2 text-sm opacity-80 max-w-prose">
              {report.tds_description}
            </p>
          </div>
          <div className="text-right">
            <div className="label">Archetype</div>
            <div className="mt-1 text-xl font-semibold">{report.archetype}</div>
            <p className="mt-1 max-w-xs text-xs opacity-75">
              {report.archetype_description}
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Metric label="Actual TS%" value={pct(report.actual_ts)} />
        <Metric label="Predicted TS%" value={pct(report.predicted_ts)} />
        <Metric
          label="Residual"
          value={`${residualPct >= 0 ? "+" : ""}${residualPct.toFixed(1)} pts`}
          subtitle={
            residualPct >= 0
              ? "Outperforming expectation"
              : "Underperforming expectation"
          }
          tone={residualPct >= 0 ? "good" : "bad"}
        />
      </div>

      <div className="card p-6">
        <h3 className="text-sm font-semibold text-slate-300">Scouting Summary</h3>
        <p className="mt-3 text-sm leading-relaxed text-slate-200 whitespace-pre-wrap">
          {report.scouting_summary}
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <RecCard title="Deployment" body={report.gm_recommendations.deployment} />
        <RecCard title="Acquisition" body={report.gm_recommendations.acquisition} />
        <RecCard title="Market Value" body={report.gm_recommendations.market_value} />
        <RecCard title="Development" body={report.gm_recommendations.development} />
      </div>

      <details className="card p-5">
        <summary className="cursor-pointer text-sm font-medium text-slate-300">
          Feature breakdown
        </summary>
        <div className="mt-4 grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
          {Object.entries(report.feature_values).map(([k, v]) => (
            <div
              key={k}
              className="flex items-center justify-between rounded-lg border border-white/5 bg-slate-900/50 px-3 py-2"
            >
              <span className="text-slate-400">{k}</span>
              <span className="font-mono text-slate-100">
                {typeof v === "number" ? v.toFixed(3) : v}
              </span>
            </div>
          ))}
        </div>
      </details>
    </div>
  );
}

function Metric({
  label,
  value,
  subtitle,
  tone,
}: {
  label: string;
  value: string;
  subtitle?: string;
  tone?: "good" | "bad";
}) {
  const toneClass =
    tone === "good"
      ? "text-emerald-300"
      : tone === "bad"
      ? "text-rose-300"
      : "text-slate-100";
  return (
    <div className="card p-5">
      <div className="label">{label}</div>
      <div className={`mt-2 text-3xl font-semibold ${toneClass}`}>{value}</div>
      {subtitle && <div className="mt-1 text-xs text-slate-400">{subtitle}</div>}
    </div>
  );
}

function RecCard({ title, body }: { title: string; body: string }) {
  return (
    <div className="card p-5">
      <div className="label">{title}</div>
      <p className="mt-2 text-sm leading-relaxed text-slate-200">{body}</p>
    </div>
  );
}
