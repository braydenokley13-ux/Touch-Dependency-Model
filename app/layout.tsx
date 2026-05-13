import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Touch Dependency Model",
  description:
    "Evaluate basketball player touch dependency, archetype, and scouting outlook with the TDM ensemble model.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="bg-slate-950 text-slate-100 font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
