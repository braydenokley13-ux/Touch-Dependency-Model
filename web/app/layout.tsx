import type { Metadata } from "next";
import { Inter, Space_Grotesk } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const display = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-display",
  display: "swap",
});

export const metadata: Metadata = {
  title: "TDM — Prospect Evaluation Engine",
  description:
    "A modern scouting tool that scores how a player's efficiency scales across roles, classifies archetype, and generates actionable reports.",
  openGraph: {
    title: "TDM — Prospect Evaluation Engine",
    description:
      "Score how efficiency scales across roles, classify archetypes, and produce scouting-grade reports in seconds.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${display.variable}`}>
      <body className="font-sans bg-aurora min-h-screen">
        <div className="fixed inset-0 -z-10 bg-grid pointer-events-none" />
        {children}
      </body>
    </html>
  );
}
