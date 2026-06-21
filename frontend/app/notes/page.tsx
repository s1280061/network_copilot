"use client";

import { useState } from "react";
import notesData from "@/lib/notes.json";

type Note = {
  slug: string;
  title: string;
  category: string;
  description: string;
  file: string;
  icon: string;
  updated: string;
  source?: string;
};

const NOTES = notesData as Note[];

export default function NotesPage() {
  const [active, setActive] = useState<Note | null>(NOTES[0] ?? null);

  return (
    <div className="space-y-6">
      <header>
        <div className="flex items-center gap-3 mb-1">
          <span className="text-3xl">📕</span>
          <h1 className="text-2xl font-bold">PDFノート</h1>
        </div>
        <p className="text-slate-500 text-sm">
          LaTeXで作成した講義レジュメ形式のノート（engineering-notes）をPDFで閲覧・ダウンロードできます。
        </p>
      </header>

      {NOTES.length === 0 && (
        <p className="text-slate-400 text-sm">まだノートがありません。</p>
      )}

      {/* note list */}
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {NOTES.map((n) => (
          <button
            key={n.slug}
            onClick={() => setActive(n)}
            className={`text-left border rounded-xl bg-white p-4 transition hover:shadow-md ${
              active?.slug === n.slug
                ? "border-sky-400 ring-1 ring-sky-200"
                : "hover:border-sky-300"
            }`}
          >
            <div className="flex items-center gap-2 mb-2">
              <span className="text-2xl">{n.icon}</span>
              <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-600">
                {n.category}
              </span>
            </div>
            <h3 className="font-semibold leading-snug">{n.title}</h3>
            <p className="text-sm text-slate-500 mt-1 line-clamp-3">
              {n.description}
            </p>
            <p className="text-xs text-slate-400 mt-2">更新: {n.updated}</p>
          </button>
        ))}
      </div>

      {/* inline viewer */}
      {active && (
        <section className="border rounded-xl bg-white overflow-hidden">
          <div className="flex items-center justify-between gap-3 px-4 py-3 border-b bg-slate-50">
            <div className="flex items-center gap-2 min-w-0">
              <span className="text-xl shrink-0">{active.icon}</span>
              <h2 className="font-semibold truncate">{active.title}</h2>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <a
                href={active.file}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm rounded-md px-3 py-1.5 border border-slate-300 text-slate-600 hover:bg-white"
              >
                別タブで開く ↗
              </a>
              <a
                href={active.file}
                download
                className="text-sm rounded-md px-3 py-1.5 bg-sky-600 text-white hover:bg-sky-700"
              >
                ダウンロード ↓
              </a>
            </div>
          </div>
          <object
            data={`${active.file}#view=FitH`}
            type="application/pdf"
            className="w-full"
            style={{ height: "80vh" }}
          >
            <div className="p-6 text-sm text-slate-500">
              このブラウザはPDFのインライン表示に対応していません。
              <a
                href={active.file}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sky-600 underline ml-1"
              >
                こちらから開いてください
              </a>
              。
            </div>
          </object>
          {active.source && (
            <div className="px-4 py-2 border-t text-xs text-slate-400">
              ソース:{" "}
              <a
                href={active.source}
                target="_blank"
                rel="noopener noreferrer"
                className="text-sky-600 hover:underline"
              >
                {active.source}
              </a>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
