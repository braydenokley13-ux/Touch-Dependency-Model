"use client";

import { useState } from "react";
import type { EvaluationReport, PlayerStats } from "@/lib/types";

interface Field {
  key: keyof PlayerStats | string;
  label: string;
  hint?: string;
  type?: "number" | "text" | "select";
  step?: string;
  required?: boolean;
  options?: string[];
}

const FIELDS: Record<string, Field[]> = {
  Identity: [
    { key: "Player", label: "Player Name", type: "text" },
    { key: "Age", label: "Age", type: "number" },
    {
      key: "Pos",
      label: "Position",
      type: "select",
      options: ["", "G", "F", "C", "PG", "SG", "SF", "PF", "G-F", "F-C"],
    },
  ],
  Shooting: [
    { key: "FG", label: "FG", required: true },
    { key: "FGA", label: "FGA", required: true },
    { key: "3P", label: "3P" },
    { key: "3PA", label: "3PA" },
    { key: "FT", label: "FT", required: true },
    { key: "FTA", label: "FTA", required: true },
  ],
  Production: [
    { key: "PTS", label: "Points", required: true },
    { key: "MP", label: "Minutes Played", required: true },
    { key: "AST", label: "Assists" },
    { key: "TOV", label: "Turnovers" },
  ],
  Advanced: [
    { key: "USG%", label: "Usage % (optional)", step: "0.1" },
    { key: "AST%", label: "Assist % (optional)", step: "0.1" },
  ],
};

const PRESETS: Record<string, Partial<PlayerStats>> = {
  "Star Guard": {
    Player: "Star Guard",
    FG: 700, FGA: 1500, "3P": 220, "3PA": 600,
    FT: 400, FTA: 480, PTS: 2020, MP: 2700,
    AST: 600, TOV: 240, Age: 27, Pos: "G",
  },
  "Sharpshooter": {
    Player: "Sharpshooter",
    FG: 280, FGA: 620, "3P": 180, "3PA": 440,
    FT: 90, FTA: 100, PTS: 830, MP: 2200,
    AST: 110, TOV: 70, Age: 28, Pos: "G",
  },
  "Stretch Big": {
    Player: "Stretch Big",
    FG: 320, FGA: 650, "3P": 90, "3PA": 240,
    FT: 150, FTA: 190, PTS: 880, MP: 2100,
    AST: 110, TOV: 90, Age: 26, Pos: "F",
  },
  "Role Player": {
    Player: "Role Player",
    FG: 180, FGA: 400, "3P": 60, "3PA": 170,
    FT: 80, FTA: 100, PTS: 500, MP: 1800,
    AST: 90, TOV: 60, Age: 27, Pos: "F",
  },
};

interface Props {
  onResult: (report: EvaluationReport) => void;
  onError: (message: string) => void;
  setLoading: (loading: boolean) => void;
  loading: boolean;
}

export default function PlayerForm({
  onResult,
  onError,
  setLoading,
  loading,
}: Props) {
  const [values, setValues] = useState<Record<string, string>>({
    Player: "Sample Player",
    FG: "373",
    FGA: "1024",
    "3P": "50",
    "3PA": "150",
    FT: "285",
    FTA: "374",
    PTS: "1031",
    MP: "2800",
    AST: "247",
    TOV: "150",
    Age: "25",
    Pos: "G",
  });

  function update(key: string, value: string) {
    setValues((prev) => ({ ...prev, [key]: value }));
  }

  function applyPreset(name: string) {
    const preset = PRESETS[name];
    if (!preset) return;
    const next: Record<string, string> = {};
    for (const [k, v] of Object.entries(preset)) {
      next[k] = String(v);
    }
    setValues(next);
  }

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setLoading(true);
    onError("");

    const payload: Record<string, string | number> = {};
    for (const [k, v] of Object.entries(values)) {
      if (v === "" || v === undefined) continue;
      payload[k] = v;
    }

    try {
      const response = await fetch("/api/evaluate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) {
        onError(data.error || `Request failed (${response.status})`);
        return;
      }
      onResult(data as EvaluationReport);
    } catch (err) {
      onError(err instanceof Error ? err.message : "Network error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="card p-6 space-y-6">
      <div className="flex items-center justify-between gap-3 flex-wrap">
        <div>
          <h2 className="text-lg font-semibold">Player Statistics</h2>
          <p className="text-sm text-slate-400">
            Enter season totals. Required fields are marked with{" "}
            <span className="text-court-500">*</span>.
          </p>
        </div>
        <div className="flex gap-2 flex-wrap">
          {Object.keys(PRESETS).map((name) => (
            <button
              key={name}
              type="button"
              onClick={() => applyPreset(name)}
              className="btn-ghost"
            >
              {name}
            </button>
          ))}
        </div>
      </div>

      {Object.entries(FIELDS).map(([group, fields]) => (
        <div key={group}>
          <h3 className="text-xs font-semibold uppercase tracking-wider text-slate-500 mb-3">
            {group}
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {fields.map((field) => (
              <div key={field.key as string}>
                <label className="label" htmlFor={field.key as string}>
                  {field.label}
                  {field.required && (
                    <span className="text-court-500"> *</span>
                  )}
                </label>
                {field.type === "select" ? (
                  <select
                    id={field.key as string}
                    className="input"
                    value={values[field.key as string] ?? ""}
                    onChange={(e) =>
                      update(field.key as string, e.target.value)
                    }
                  >
                    {(field.options ?? []).map((opt) => (
                      <option key={opt} value={opt}>
                        {opt || "—"}
                      </option>
                    ))}
                  </select>
                ) : (
                  <input
                    id={field.key as string}
                    className="input"
                    type={field.type ?? "number"}
                    step={field.step ?? (field.type === "text" ? undefined : "1")}
                    min={field.type === "text" ? undefined : 0}
                    value={values[field.key as string] ?? ""}
                    onChange={(e) =>
                      update(field.key as string, e.target.value)
                    }
                    required={field.required}
                  />
                )}
              </div>
            ))}
          </div>
        </div>
      ))}

      <div className="flex justify-end gap-3 pt-2">
        <button type="submit" disabled={loading} className="btn-primary">
          {loading ? "Evaluating…" : "Evaluate Player"}
        </button>
      </div>
    </form>
  );
}
