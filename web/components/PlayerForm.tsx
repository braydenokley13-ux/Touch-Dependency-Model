"use client";

import { PlayerStats } from "@/lib/types";

interface Props {
  stats: PlayerStats;
  onChange: (stats: PlayerStats) => void;
}

const POSITIONS = ["PG", "SG", "SF", "PF", "C", "G", "F"];

export function PlayerForm({ stats, onChange }: Props) {
  const update = <K extends keyof PlayerStats>(key: K, value: PlayerStats[K]) =>
    onChange({ ...stats, [key]: value });

  const num = (key: keyof PlayerStats) => (e: React.ChangeEvent<HTMLInputElement>) => {
    const v = e.target.value;
    update(key, (v === "" ? undefined : Number(v)) as any);
  };

  return (
    <div className="space-y-6">
      <Row label="Identity">
        <Field label="Name" cols={2}>
          <input
            type="text"
            value={stats.name ?? ""}
            onChange={(e) => update("name", e.target.value)}
            placeholder="Prospect"
          />
        </Field>
        <Field label="Age">
          <input
            type="number"
            min={16}
            max={45}
            value={stats.age ?? ""}
            onChange={num("age")}
          />
        </Field>
        <Field label="Position">
          <select
            value={stats.position ?? "SF"}
            onChange={(e) => update("position", e.target.value)}
          >
            {POSITIONS.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </Field>
      </Row>

      <Row label="Volume">
        <Field label="Minutes (MP)">
          <input type="number" min={1} value={stats.mp} onChange={num("mp")} />
        </Field>
        <Field label="Points (PTS)">
          <input type="number" min={0} value={stats.pts} onChange={num("pts")} />
        </Field>
        <Field label="Assists (AST)">
          <input type="number" min={0} value={stats.ast ?? 0} onChange={num("ast")} />
        </Field>
        <Field label="Turnovers (TOV)">
          <input type="number" min={0} value={stats.tov ?? 0} onChange={num("tov")} />
        </Field>
      </Row>

      <Row label="Shooting">
        <Field label="FG">
          <input type="number" min={0} value={stats.fg} onChange={num("fg")} />
        </Field>
        <Field label="FGA">
          <input type="number" min={1} value={stats.fga} onChange={num("fga")} />
        </Field>
        <Field label="3P">
          <input type="number" min={0} value={stats.threeP ?? 0} onChange={num("threeP")} />
        </Field>
        <Field label="3PA">
          <input type="number" min={0} value={stats.threePA ?? 0} onChange={num("threePA")} />
        </Field>
        <Field label="FT">
          <input type="number" min={0} value={stats.ft} onChange={num("ft")} />
        </Field>
        <Field label="FTA">
          <input type="number" min={0} value={stats.fta} onChange={num("fta")} />
        </Field>
      </Row>
    </div>
  );
}

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <div className="section-label mb-3">{label}</div>
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">{children}</div>
    </div>
  );
}

function Field({
  label,
  cols = 1,
  children,
}: {
  label: string;
  cols?: number;
  children: React.ReactNode;
}) {
  const span = cols === 2 ? "sm:col-span-2" : "";
  return (
    <label className={`block ${span}`}>
      <span className="mb-1.5 block text-[11px] font-medium uppercase tracking-wider text-white/45">
        {label}
      </span>
      {children}
    </label>
  );
}
