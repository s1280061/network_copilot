"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { getHome, chat, search as apiSearch, IS_STATIC } from "@/lib/api";
import { Home, Ref, SearchHit } from "@/lib/types";
import ArticleCard from "@/components/home/ArticleCard";
import { useProfileRecommend } from "@/lib/profile";

export default function HomePage() {
  const router = useRouter();
  const [home, setHome] = useState<Home | null>(null);
  const [q, setQ] = useState("");
  const [asking, setAsking] = useState(false);
  const [answer, setAnswer] = useState<string | null>(null);
  const [sources, setSources] = useState<Ref[]>([]);
  const [fallbackHits, setFallbackHits] = useState<SearchHit[] | null>(null);
  const recommend = useProfileRecommend(home);

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
        // No backend: keyword search over articles instead of AI.
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
    <div className="space-y-8">
      <header>
        <h1 className="text-2xl font-bold">ADAS技術コパイロット</h1>
        <p className="text-slate-500 text-sm mt-1">
          車載ネットワークの技術質問にAIが回答し、関連記事へ案内します。
        </p>
      </header>

      {/* technical question box */}
      <div>
        <div className="flex gap-2">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && ask()}
            placeholder="技術質問を入力 (例: 車載でUDPが使われる理由 / SOME/IPとROS2 DDSの違い)"
            className="flex-1 border rounded-lg px-4 py-2.5"
          />
          <button
            onClick={ask}
            disabled={asking}
            className="bg-sky-600 text-white px-6 rounded-lg disabled:opacity-50"
          >
            質問する
          </button>
        </div>
        {IS_STATIC && (
          <p className="text-xs text-slate-400 mt-1">
            ※ 現在は記事閲覧モードのため、AI回答の代わりにキーワード検索を行います(バックエンド接続でAI有効化)。
          </p>
        )}
      </div>

      {asking && <p className="text-slate-400 text-sm">考え中...</p>}

      {answer && (
        <section className="border rounded-xl bg-white p-4">
          <div className="flex items-center justify-between mb-2">
            <h2 className="font-semibold">🤖 AIの回答</h2>
            <button onClick={clearAsk} className="text-xs text-slate-400 hover:text-slate-600">
              クリア
            </button>
          </div>
          <p className="whitespace-pre-wrap text-sm">{answer}</p>
          {sources.length > 0 && (
            <div className="mt-3 pt-3 border-t flex flex-wrap gap-2">
              <span className="text-xs text-slate-400 w-full">📚 参考記事:</span>
              {sources.map((s) => (
                <button
                  key={s.slug}
                  onClick={() => router.push(`/glossary/${s.slug}`)}
                  className="text-xs bg-sky-100 text-sky-700 rounded px-2 py-1 hover:bg-sky-200"
                >
                  {s.title} →
                </button>
              ))}
            </div>
          )}
        </section>
      )}

      {fallbackHits !== null && (
        <section className="border rounded-xl bg-white p-4">
          <div className="flex items-center justify-between mb-2">
            <h2 className="font-semibold">検索結果</h2>
            <button onClick={clearAsk} className="text-xs text-slate-400 hover:text-slate-600">
              クリア
            </button>
          </div>
          {fallbackHits.length === 0 && (
            <p className="text-sm text-slate-400">該当する記事がありません。</p>
          )}
          <ul className="space-y-1">
            {fallbackHits.map((h) => (
              <li key={h.slug}>
                <Link
                  href={`/glossary/${h.slug}`}
                  className="flex items-center justify-between rounded px-2 py-1.5 hover:bg-slate-50"
                >
                  <span className="font-medium">{h.title}</span>
                  <span className="text-xs text-slate-400">{h.category}</span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      )}

      {!home && <p className="text-slate-400">読み込み中...</p>}

      {home && (
        <>
          {/* personalized recommendations */}
          {recommend.length > 0 && (
            <section>
              <h2 className="font-bold mb-3">✨ あなたへのおすすめ</h2>
              <div className="flex gap-3 overflow-x-auto pb-2">
                {recommend.map((a) => (
                  <ArticleCard key={a.slug} a={a} />
                ))}
              </div>
            </section>
          )}

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
