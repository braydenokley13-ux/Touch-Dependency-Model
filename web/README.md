# TDM — Web

A Next.js 14 App Router frontend for the Touch Dependency Model. The entire
scoring pipeline is ported to TypeScript so the app runs fully client-side and
ships as a static bundle — deploy anywhere, but it's optimized for Vercel.

## Stack

- Next.js 14 (App Router, React 18)
- TypeScript
- Tailwind CSS
- Framer Motion for entrance animations
- Recharts for the radar fingerprint
- Lucide icons

## Local development

```bash
cd web
npm install
npm run dev
```

Open http://localhost:3000.

## Production build

```bash
npm run build
npm run start
```

The `/` route is prerendered as static HTML — no server runtime required.

## Deploy to Vercel

1. Push this repo to GitHub.
2. In Vercel, import the repo and set the **Root Directory** to `web/`.
3. Framework preset is auto-detected as Next.js. Leave the defaults.
4. Deploy.

No environment variables are needed — the evaluation model runs entirely in the
browser.

## Project layout

```
web/
├── app/                    # App Router entry
│   ├── layout.tsx
│   ├── page.tsx
│   └── globals.css
├── components/             # UI components
│   ├── Hero.tsx
│   ├── Workbench.tsx
│   ├── PlayerForm.tsx
│   ├── ResultsPanel.tsx
│   ├── TDSDial.tsx
│   ├── EfficiencyComparison.tsx
│   ├── RadarFingerprint.tsx
│   ├── MethodologySection.tsx
│   ├── EmptyState.tsx
│   └── Footer.tsx
└── lib/                    # TypeScript TDM logic
    ├── tdm.ts              # Top-level evaluatePlayer()
    ├── features.ts         # Feature engineering
    ├── model.ts            # Expected TS% + TDS percentile
    ├── archetypes.ts       # 12 offensive archetypes
    ├── scouting.ts         # Narrative summary generation
    ├── recommendations.ts  # Deployment / acquisition / etc.
    ├── presets.ts          # Example prospects
    ├── types.ts
    └── utils.ts
```

## How it works

1. Box-score stats are transformed into USG%, AST%, TOV%, shot-diet rates, and per-36 volume metrics.
2. A deterministic regression surface predicts expected TS% from touch load and shot selection.
3. The residual (actual − expected TS%) is mapped to a TDS score (0–100) via a normal-CDF percentile.
4. A rule-based classifier assigns one of 12 offensive archetypes.
5. Natural-language summaries and front-office recommendations are synthesized from the profile.
