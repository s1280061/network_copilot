"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getHome, chat, search as apiSearch, IS_STATIC } from "@/lib/api";
import { Home, Ref, SearchHit } from "@/lib/types";
import ArticleCard from "@/components/home/ArticleCard";

export default function HomePage() {
  const router = useRouter();
  const [home, setHome] = useState<Home | null>(null);
  const [q, setQ] = useState("");
  const [asking, setAsking] = useState(false);
  const [answer, setAnswer] = useState<string | null>(null);
  const [sources, setSources] = useState<Ref[]>([]);
  const [fallbackHits, setFallbackHits] = useState<SearchHit[] | null>(null);

  useEffect(() => {
    getHome().then(setHome).catch(() => {});
  }, []);

  async function ask() {
    if (!q.trim() || asking) return;
    setAsking(true);
    setAnswer(null);
    setSources([]);
    setFallbackHits(null);
    try {
      if (IS_STATIC) {
        const d = await apiSearch(q);
        setFallbackHits(d.results);
      } else {
        const { answer, sources } = await chat(q);
        setAnswer(answer);
        setSources(sources);
      }
    } catch {
      setAnswer("エラー: 回答を取得できませんでした。");
    } finally {
      setAsking(false);
    }
  }

  function clearAsk() {
    setQ("");
    setAnswer(null);
    setSources([]);
    setFallbackHits(null);
  }

  return (
    <div className="space-y-10">
      <header>
        <h1 className="text-2xl font-bold">Network Copilot</h1>
        <p className="text-slate-500 text-sm mt-1">
          車載ネットワーク・データサイエンスの技術記事サイトです。
        </p>
      </header>

      {/* search / AI chat */}
      <div>
        <div className="flex gap-2">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && ask()}
            placeholder="記事を検索、または技術質問を入力..."
            className="flex-1 border rounded-lg px-4 py-2.5 text-sm"
          />
          <button
            onClick={ask}
            disabled={asking}
            className="bg-sky-600 text-white px-6 rounded-lg text-sm disabled:opacity-50"
          >
            {asking ? "..." : "検索"}
          </button>
        </div>
      </div>

      {answer && (
        <section className="border rounded-xl bg-white p-5">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold text-sm">AI の回答</h2>
            <button onClick={clearAsk} className="text-xs text-slate-400 hover:text-slate-600">クリア</button>
          </div>
          <p className="whitespace-pre-wrap text-sm leading-relaxed">{answer}</p>
          {sources.length > 0 && (
            <div className="mt-4 pt-3 border-t flex flex-wrap gap-2">
              {sources.map((s) => (
                <button
                  key={s.slug}
                  onClick={() => router.push(`/glossary/${s.slug}`)}
                  className="text-xs bg-sky-50 text-sky-700 rounded-full px-3 py-1 hover:bg-sky-100"
                >
                  {s.title} →
                </button>
              ))}
            </div>
          )}
        </section>
      )}

      {fallbackHits !== null && (
        <section className="border rounded-xl bg-white p-5">
          <div className="flex items-center justify-between mb-3">
            <h2 className="font-semibold text-sm">検索結果</h2>
            <button onClick={clearAsk} className="text-xs text-slate-400 hover:text-slate-600">クリア</button>
          </div>
          {fallbackHits.length === 0 && <p className="text-sm text-slate-400">該当する記事がありません。</p>}
          <ul className="space-y-1">
            {fallbackHits.map((h) => (
              <li key={h.slug}>
                <Link
                  href={`/glossary/${h.slug}`}
                  className="flex items-center justify-between rounded-lg px-3 py-2 hover:bg-slate-50"
                >
                  <span className="font-medium text-sm">{h.title}</span>
                  <span className="text-xs text-slate-400">{h.category}</span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      {!home && <p className="text-slate-400 text-sm">読み込み中...</p>}

      {home && home.categories
        .filter((c) => c.articles.length > 0)
        .map((c) => (
          <section key={c.name}>
            <div className="flex items-center justify-between mb-3">
              <h2 className="font-bold">{c.name}</h2>
              <Link href={`/glossary?cat=${c.name}`} className="text-xs text-sky-600 hover:underline">
                すべて見る →
              </Link>
            </div>
            <div className="flex flex-col sm:flex-row gap-3 sm:overflow-x-auto pb-2">
              {c.articles.slice(0, 6).map((a) => (
                <ArticleCard key={a.slug} a={a} />
              ))}
            </div>
          </section>
        ))}
    </div>
  );
}
