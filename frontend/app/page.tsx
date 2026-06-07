"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getHome, search as apiSearch } from "@/lib/api";
import { Home, SearchHit } from "@/lib/types";
import ArticleCard from "@/components/home/ArticleCard";

export default function HomePage() {
  const router = useRouter();
  const [home, setHome] = useState<Home | null>(null);
  const [q, setQ] = useState("");
  const [hits, setHits] = useState<SearchHit[] | null>(null);
  const [searching, setSearching] = useState(false);

  useEffect(() => {
    getHome().then(setHome).catch(() => {});
  }, []);

  async function runSearch() {
    if (!q.trim()) {
      setHits(null);
      return;
    }
    setSearching(true);
    try {
      const d = await apiSearch(q);
      setHits(d.results);
    } catch {
      setHits([]);
    } finally {
      setSearching(false);
    }
  }

  return (
    <div className="space-y-8">
      <header>
        <h1 className="text-2xl font-bold">ADAS技術 note</h1>
        <p className="text-slate-500 text-sm mt-1">
          ネットワーク・車載通信の記事を、カテゴリと意味検索で探せます。
        </p>
      </header>

      {/* semantic search */}
      <div className="flex gap-2">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && runSearch()}
          placeholder="意味で検索 (例: 低遅延な通信, パケットを解析したい)"
          className="flex-1 border rounded-lg px-4 py-2"
        />
        <button
          onClick={runSearch}
          className="bg-sky-600 text-white px-5 rounded-lg"
        >
          検索
        </button>
      </div>

      {hits !== null && (
        <section className="border rounded-xl bg-white p-4">
          <div className="flex items-center justify-between mb-2">
            <h2 className="font-semibold">検索結果</h2>
            <button
              onClick={() => {
                setHits(null);
                setQ("");
              }}
              className="text-xs text-slate-400 hover:text-slate-600"
            >
              クリア
            </button>
          </div>
          {searching && <p className="text-sm text-slate-400">検索中...</p>}
          {!searching && hits.length === 0 && (
            <p className="text-sm text-slate-400">該当する記事がありません。</p>
          )}
          <ul className="space-y-1">
            {hits.map((h) => (
              <li key={h.slug}>
                <Link
                  href={`/glossary/${h.slug}`}
                  className="flex items-center justify-between rounded px-2 py-1.5 hover:bg-slate-50"
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
        </section>
      )}

      {!home && <p className="text-slate-400">読み込み中...</p>}

      {home && (
        <>
          {/* ranking */}
          {home.ranking.length > 0 && (
            <section>
              <h2 className="font-bold mb-3">🔥 人気記事ランキング</h2>
              <ol className="border rounded-xl bg-white divide-y">
                {home.ranking.map((r, i) => (
                  <li key={r.slug}>
                    <Link
                      href={`/glossary/${r.slug}`}
                      className="flex items-center gap-3 px-4 py-2.5 hover:bg-slate-50"
                    >
                      <span
                        className={`w-6 text-center font-bold ${
                          i < 3 ? "text-sky-600" : "text-slate-400"
                        }`}
                      >
                        {i + 1}
                      </span>
                      <span className="flex-1 font-medium">{r.title}</span>
                      <span className="text-xs text-slate-400">👁 {r.views}</span>
                    </Link>
                  </li>
                ))}
              </ol>
            </section>
          )}

          {/* categories */}
          {home.categories
            .filter((c) => c.articles.length > 0)
            .map((c) => (
              <section key={c.name}>
                <h2 className="font-bold mb-3">{c.name}</h2>
                <div className="flex gap-3 overflow-x-auto pb-2">
                  {c.articles.map((a) => (
                    <ArticleCard key={a.slug} a={a} />
                  ))}
                </div>
              </section>
            ))}
        </>
      )}
    </div>
  );
}
