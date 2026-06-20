"use client";

import Link from "next/link";
import { useStudyPanel } from "@/lib/study-context";

export default function StudyPanel() {
  const { panel } = useStudyPanel();
  const items = panel.related ?? [];

  return (
    <aside className="w-60 shrink-0 border-l bg-white overflow-y-auto p-4 hidden lg:block">
      <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-3">
        関連記事
      </h2>

      {items.length === 0 && (
        <p className="text-sm text-slate-400">
          記事を開くと関連記事がここに表示されます。
        </p>
      )}

      <div className="flex flex-col gap-1">
        {items.map((it) => (
          <Link
            key={it.slug}
            href={`/glossary/${it.slug}`}
            className="text-sm text-slate-600 hover:text-sky-600 hover:bg-slate-50 rounded-md px-2 py-1.5 transition-colors"
          >
            {it.title}
          </Link>
        ))}
      </div>
    </aside>
  );
}
