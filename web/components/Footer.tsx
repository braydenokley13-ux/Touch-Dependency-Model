"use client";

export function Footer() {
  return (
    <footer className="mt-24 border-t border-white/5 pt-8 text-sm text-white/45">
      <div className="flex flex-col items-start justify-between gap-4 sm:flex-row sm:items-center">
        <div>
          <div className="font-display text-sm font-semibold text-white/80">
            Touch Dependency Model
          </div>
          <div className="mt-1 text-xs text-white/40">
            Deterministic scouting analytics · Runs entirely on the client
          </div>
        </div>
        <div className="flex items-center gap-6 text-xs uppercase tracking-[0.18em] text-white/40">
          <a
            href="https://github.com/braydenokley13-ux/touch-dependency-model"
            target="_blank"
            rel="noreferrer"
            className="hover:text-white"
          >
            Source
          </a>
          <a href="#evaluate" className="hover:text-white">Evaluate</a>
          <a href="#methodology" className="hover:text-white">Method</a>
        </div>
      </div>
    </footer>
  );
}
