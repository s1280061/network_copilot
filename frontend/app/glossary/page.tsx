"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getArticles, search as apiSearch } from "@/lib/api";
import { Article, SearchHit } from "@/lib/types";
import Thumbnail, { categoryStyle } from "@/components/Thumbnail";

const CATEGORIES = ["Ethernet", "TCP/IP", "PCAP", "SOME/IP", "AUTOSAR", "SDV", "Automotive Bus", "Diagnostics", "Security", "Howto", "Python", "ML", "DL", "GenAI", "CV", "Electronics", "Automotive", "Wireless"];

export default function GlossaryPage() {
  const [items, setItems] = useState<Article[]>([]);
  const [q, setQ] = useState("");
  const [hits, setHits] = useState<SearchHit[] | null>(null);
  const [mode, setMode] = useState("");
  const [activeTab, setActiveTab] = useState("all");

  useEffect(() => {
    getArticles().then((d) => setItems(d.articles)).catch(() => {});
  }, []);

  async function runSearch() {
    if (!q.trim()) { setHits(null); return; }
    const d = await apiSearch(q);
    setHits(d.results);
    setMode(d.mode);
  }

  const displayed = activeTab === "all"
    ? items
    : items.filter((a) => a.category === activeTab);

  return (
    <div>
      <header className="mb-5">
        <h1 className="text-2xl font-bold">記事一覧</h1>
      </header>

      <div className="flex gap-2 mb-5">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && runSearch()}
          placeholder="キーワードで検索..."
          className="flex-1 border rounded-lg px-4 py-2 text-sm"
        />
        <button onClick={runSearch} className="bg-sky-600 text-white px-5 rounded-lg text-sm">
          検索
        </button>
      </div>

      {hits !== null ? (
        <div>
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm text-slate-500">
              {hits.length} 件（{mode === "semantic" ? "意味検索" : "キーワード"}）
            </p>
            <button onClick={() => { setHits(null); setQ(""); }} className="text-xs text-slate-400 hover:text-slate-600">
              一覧に戻る
            </button>
          </div>
          {hits.length === 0 && <p className="text-sm text-slate-400">該当する記事がありません。</p>}
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {hits.map((h) => {
              const art = items.find((a) => a.slug === h.slug);
              const style = categoryStyle(h.category ?? "");
              return (
                <Link
                  key={h.slug}
                  href={`/glossary/${h.slug}`}
                  className="block border rounded-xl bg-white overflow-hidden hover:border-sky-400 hover:shadow-sm transition"
                >
                  {art && <Thumbnail slug={art.slug} category={art.category} className="h-28 w-full" />}
                  <div className="p-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${style.bg} ${style.text}`}>{h.category}</span>
                    <p className="font-semibold text-sm mt-2">{h.title}</p>
                    {art?.excerpt && <p className="text-xs text-slate-500 mt-1 line-clamp-2">{art.excerpt}</p>}
                  </div>
                </Link>
              );
            })}
          </div>
        </div>
      ) : (
        <>
          {/* Category tabs */}
          <div className="flex gap-2 flex-wrap mb-5">
            <button
              onClick={() => setActiveTab("all")}
              className={`text-xs px-3 py-1.5 rounded-full border transition ${activeTab === "all" ? "bg-slate-800 text-white border-slate-800" : "bg-white text-slate-600 hover:border-slate-400"}`}
            >
              すべて
            </button>
            {CATEGORIES.map((c) => {
              const style = categoryStyle(c);
              return (
                <button
                  key={c}
                  onClick={() => setActiveTab(c)}
                  className={`text-xs px-3 py-1.5 rounded-full border transition ${activeTab === c ? `${style.bg} ${style.text} border-transparent` : "bg-white text-slate-600 hover:border-slate-400"}`}
                >
                  {c}
                </button>
              );
            })}
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {displayed.map((a) => {
              const style = categoryStyle(a.category);
              return (
                <Link
                  key={a.slug}
                  href={`/glossary/${a.slug}`}
                  className="block border rounded-xl bg-white overflow-hidden hover:border-sky-400 hover:shadow-sm transition"
                >
                  <Thumbnail slug={a.slug} category={a.category} className="h-28 w-full" />
                  <div className="p-3">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${style.bg} ${style.text}`}>{a.category}</span>
                    <h2 className="font-semibold text-sm mt-2">{a.title}</h2>
                    <p className="text-xs text-slate-500 mt-1 line-clamp-2">{a.excerpt}</p>
                  </div>
                </Link>
              );
            })}
          </div>
        </>
      )}
    </div>
  );
}
