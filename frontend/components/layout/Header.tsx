"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getRoadmap } from "@/lib/api";

export default function Header() {
  const [pct, setPct] = useState(0);

  useEffect(() => {
    const load = () =>
      getRoadmap()
        .then((d) =>
          setPct(
            d.progress.total
              ? Math.round((d.progress.completed / d.progress.total) * 100)
              : 0
          )
        )
        .catch(() => {});
    load();
    const id = setInterval(load, 4000);
    return () => clearInterval(id);
  }, []);

  return (
    <header className="h-14 shrink-0 bg-slate-900 text-white flex items-center justify-between px-6">
      <Link href="/" className="font-bold tracking-tight">
        📡 Network Learning Copilot
      </Link>
      <div className="flex items-center gap-3 text-sm">
        <span className="text-slate-300">学習進捗</span>
        <div className="w-40 h-2 bg-slate-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-sky-400 transition-all"
            style={{ width: `${pct}%` }}
          />
        </div>
        <span className="tabular-nums w-10 text-right">{pct}%</span>
      </div>
    </header>
  );
}
