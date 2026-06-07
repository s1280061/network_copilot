"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getRoadmap } from "@/lib/api";
import { Roadmap } from "@/lib/types";

export default function RoadmapTree() {
  const [data, setData] = useState<Roadmap | null>(null);

  useEffect(() => {
    getRoadmap().then(setData).catch(() => {});
  }, []);

  if (!data) return <p className="text-slate-400">読み込み中...</p>;

  return (
    <div className="space-y-6">
      {data.levels.map((lv) => (
        <div key={lv.level} className="relative">
          <div className="flex items-center gap-2 mb-2">
            <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-slate-900 text-white text-xs font-bold">
              {lv.level}
            </span>
            <h2 className="font-semibold">{lv.title}</h2>
          </div>
          <p className="text-sm text-slate-500 ml-9 mb-3">{lv.description}</p>

          <ul className="ml-9 border-l-2 border-slate-200 pl-4 space-y-1.5">
            {lv.items.map((it) => (
              <li key={it.slug}>
                <Link
                  href={`/glossary/${it.slug}`}
                  className="group flex items-center gap-2 rounded-md px-2 py-1.5 hover:bg-slate-100"
                >
                  <span
                    className={`inline-flex items-center justify-center w-5 h-5 rounded-full text-xs ${
                      it.completed
                        ? "bg-green-500 text-white"
                        : "border-2 border-slate-300 text-transparent"
                    }`}
                  >
                    ✓
                  </span>
                  <span
                    className={
                      it.completed ? "text-slate-400 line-through" : "text-slate-700"
                    }
                  >
                    {it.title}
                  </span>
                  <span className="ml-auto text-xs text-slate-300 group-hover:text-sky-500">
                    開く →
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
