"use client";

import { motion } from "framer-motion";

interface Props {
  value: number; // 0-100
  category: string;
}

export function TDSDial({ value, category }: Props) {
  // Semi-circle arc from 180° to 360°
  const size = 200;
  const stroke = 14;
  const r = (size - stroke) / 2;
  const cx = size / 2;
  const cy = size / 2;
  const circ = Math.PI * r; // semicircle length
  const clamped = Math.max(0, Math.min(100, value));
  const dash = (clamped / 100) * circ;

  // Color matches TDS band
  const color =
    clamped >= 70 ? "#34d399"
      : clamped >= 55 ? "#60a5fa"
      : clamped >= 45 ? "#fbbf24"
      : clamped >= 35 ? "#fb923c"
      : "#f87171";

  const gradientId = `tds-grad-${Math.round(clamped)}`;

  return (
    <div className="flex flex-col items-center justify-center">
      <div className="relative" style={{ width: size, height: size / 2 + 20 }}>
        <svg width={size} height={size / 2 + 20} viewBox={`0 0 ${size} ${size / 2 + 20}`}>
          <defs>
            <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#f87171" />
              <stop offset="25%" stopColor="#fb923c" />
              <stop offset="50%" stopColor="#fbbf24" />
              <stop offset="75%" stopColor="#60a5fa" />
              <stop offset="100%" stopColor="#34d399" />
            </linearGradient>
          </defs>

          {/* Track */}
          <path
            d={describeArc(cx, cy, r, 180, 360)}
            fill="none"
            stroke="rgba(255,255,255,0.08)"
            strokeWidth={stroke}
            strokeLinecap="round"
          />

          {/* Value */}
          <motion.path
            d={describeArc(cx, cy, r, 180, 360)}
            fill="none"
            stroke={`url(#${gradientId})`}
            strokeWidth={stroke}
            strokeLinecap="round"
            strokeDasharray={`${dash} ${circ}`}
            initial={{ strokeDasharray: `0 ${circ}` }}
            animate={{ strokeDasharray: `${dash} ${circ}` }}
            transition={{ duration: 1.1, ease: [0.21, 0.47, 0.32, 0.98] }}
          />

          {/* Tick marks */}
          {[0, 25, 50, 75, 100].map((t) => {
            const ang = 180 + (t / 100) * 180;
            const { x: x1, y: y1 } = polar(cx, cy, r + 6, ang);
            const { x: x2, y: y2 } = polar(cx, cy, r + 12, ang);
            return (
              <line
                key={t}
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                stroke="rgba(255,255,255,0.12)"
                strokeWidth={1}
              />
            );
          })}
        </svg>

        <div className="absolute inset-0 flex items-end justify-center pb-1">
          <div className="flex flex-col items-center">
            <div className="font-display text-5xl font-bold leading-none num-gradient">
              {clamped.toFixed(0)}
            </div>
            <div className="mt-1 text-[11px] uppercase tracking-[0.18em] text-white/50">
              TDS
            </div>
          </div>
        </div>
      </div>
      <div
        className="mt-2 inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-xs font-medium"
        style={{
          borderColor: `${color}55`,
          background: `${color}15`,
          color,
        }}
      >
        <span
          className="h-1.5 w-1.5 rounded-full"
          style={{ background: color }}
        />
        {category}
      </div>
    </div>
  );
}

function polar(cx: number, cy: number, r: number, angleDeg: number) {
  const rad = ((angleDeg - 0) * Math.PI) / 180;
  return { x: cx + r * Math.cos(rad), y: cy + r * Math.sin(rad) };
}

function describeArc(
  cx: number,
  cy: number,
  r: number,
  startAngle: number,
  endAngle: number
): string {
  const start = polar(cx, cy, r, endAngle);
  const end = polar(cx, cy, r, startAngle);
  const largeArc = endAngle - startAngle <= 180 ? "0" : "1";
  return `M ${start.x} ${start.y} A ${r} ${r} 0 ${largeArc} 0 ${end.x} ${end.y}`;
}
