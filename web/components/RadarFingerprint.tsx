"use client";

import {
  Radar,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  ResponsiveContainer,
} from "recharts";
import { FeatureValues } from "@/lib/types";

interface Props {
  features: FeatureValues;
}

// Normalize each feature to 0-100 against a reasonable league band.
const bands: Record<string, [number, number]> = {
  Usage: [10, 35],
  Playmaking: [5, 35],
  Scoring: [8, 30],
  Shooting: [0.45, 0.65],
  "3PT Diet": [0.1, 0.55],
  "FT Draw": [0.1, 0.5],
};

function norm(v: number, key: keyof typeof bands) {
  const [lo, hi] = bands[key];
  return Math.max(0, Math.min(100, ((v - lo) / (hi - lo)) * 100));
}

export function RadarFingerprint({ features }: Props) {
  const data = [
    { metric: "Usage", value: norm(features.usgPct, "Usage") },
    { metric: "Playmaking", value: norm(features.astPct, "Playmaking") },
    { metric: "Scoring", value: norm(features.ptsPer36, "Scoring") },
    { metric: "Shooting", value: norm(features.tsPct, "Shooting") },
    { metric: "3PT Diet", value: norm(features.threePARate, "3PT Diet") },
    { metric: "FT Draw", value: norm(features.ftaRate, "FT Draw") },
  ];

  return (
    <div className="mt-4 h-[260px]">
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={data}>
          <defs>
            <linearGradient id="radarFill" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#fb923c" stopOpacity={0.6} />
              <stop offset="100%" stopColor="#c2410c" stopOpacity={0.2} />
            </linearGradient>
          </defs>
          <PolarGrid stroke="rgba(255,255,255,0.08)" />
          <PolarAngleAxis
            dataKey="metric"
            tick={{ fill: "rgba(255,255,255,0.55)", fontSize: 11 }}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, 100]}
            tick={false}
            axisLine={false}
          />
          <Radar
            dataKey="value"
            stroke="#fb923c"
            fill="url(#radarFill)"
            fillOpacity={1}
            strokeWidth={2}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
