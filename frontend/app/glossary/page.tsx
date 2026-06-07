"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getArticles, search as apiSearch } from "@/lib/api";
import { Article, SearchHit } from "@/lib/types";

export default function GlossaryPage() {
  const [items, setItems] = useState<Article[]>([]);
  const [q, setQ] = useState("");
  const [hits, setHits] = useState<SearchHit[] | null>(null);
  const [mode, setMode] = useState("");

  useEffect(() => {
    getArticles().then((d) => setItems(d.articles)).catch(() => {});
  }, []);

  async function runSearch() {
    if (!q.trim()) {
      setHits(null);
      return;
    }
    const d = await apiSearch(q);
    setHits(d.results);
    setMode(d.mode);
  }

  return (
    <div>
      <header className="mb-5">
        <h1 className="text-2xl font-bold">用語集</h1>
        <p className="text-slate-500 text-sm mt-1">
          各用語は記事ページです。検索は意味検索(RAG)に対応しています。
        </p>
      </header>

      <div className="flex gap-2 mb-5">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && runSearch()}
          placeholder="意味で検索 (例: 確実にデータを届ける仕組み)"
          className="flex-1 border rounded-lg px-4 py-2"
        />
        <button onClick={runSearch} className="bg-sky-600 text-white px-5 rounded-lg">
          検索
        </button>
      </div>

      {hits !== null ? (
        <div>
          <div className="flex items-center justify-between mb-2">
            <p className="text-sm text-slate-500">
              検索結果（{mode === "semantic" ? "意味検索" : "キーワード"}）
            </p>
            <button
              onClick={() => {
                setHits(null);
                setQ("");
              }}
              className="text-xs text-slate-400 hover:text-slate-600"
            >
              一覧に戻る
            </button>
          </div>
          {hits.length === 0 && (
            <p className="text-sm text-slate-400">該当する記事がありません。</p>
          )}
          <ul className="space-y-1">
            {hits.map((h) => (
              <li key={h.slug}>
                <Link
                  href={`/glossary/${h.slug}`}
                  className="flex items-center justify-between border rounded-lg px-3 py-2 bg-white hover:border-sky-400"
                >
                  <span className="font-medium">{h.title}</span>
                  <span className="text-xs text-slate-400">
                    {h.category}
                    {h.score !== undefined && ` ・類似度 ${h.score}`}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <div className="grid sm:grid-cols-2 gap-3">
          {items.map((a) => (
            <Link
              key={a.slug}
              href={`/glossary/${a.slug}`}
              className="block border rounded-lg p-4 bg-white hover:border-sky-400 hover:shadow-sm transition"
            >
              <div className="flex items-center justify-between">
                <h2 className="font-semibold">{a.title}</h2>
                <span className="text-xs text-slate-400">{a.category}</span>
              </div>
              <p className="text-sm text-slate-500 mt-1 line-clamp-2">{a.excerpt}</p>
              <div className="flex gap-2 mt-2 text-xs">
                {a.completed && <span className="text-green-600">✓ 学習済み</span>}
                {a.favorite && <span className="text-amber-600">★</span>}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}
