"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { Comment } from "@/lib/api";
import staticContent from "@/lib/static-content.json";

interface ThreadSummary {
  slug: string;
  title: string;
  category: string;
  comments: Comment[];
  lastAt: string;
}

const SC: any = staticContent;

// 記事メタデータをslugで引けるマップ
const articleMap: Record<string, { title: string; category: string }> = {};
for (const a of (SC.articles as any[])) {
  articleMap[a.slug] = { title: a.title, category: a.category };
}

function formatDate(s: string) {
  const d = new Date(s);
  if (isNaN(d.getTime())) return s;
  return `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, "0")}/${String(d.getDate()).padStart(2, "0")} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}`;
}

async function fetchAllComments(): Promise<Comment[]> {
  try {
    const res = await fetch("/api/comments", { cache: "no-store" });
    if (!res.ok) return [];
    const d = await res.json();
    return d.comments as Comment[];
  } catch {
    return [];
  }
}

export default function BoardPage() {
  const router = useRouter();
  const [threads, setThreads] = useState<ThreadSummary[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    const allComments = await fetchAllComments();

    // slug ごとにグループ化
    const grouped: Record<string, Comment[]> = {};
    for (const c of allComments) {
      (grouped[c.slug] ??= []).push(c);
    }

    const active: ThreadSummary[] = Object.entries(grouped)
      .map(([slug, comments]) => {
        const meta = articleMap[slug] ?? { title: slug, category: "" };
        // created_at 昇順に並べてから最後を「最終」とする
        const sorted = [...comments].sort((a, b) =>
          a.created_at < b.created_at ? -1 : 1
        );
        return {
          slug,
          title: meta.title,
          category: meta.category,
          comments: sorted,
          lastAt: sorted[sorted.length - 1].created_at,
        };
      })
      .sort((a, b) => (a.lastAt < b.lastAt ? 1 : -1));

    setThreads(active);
    setLoading(false);
  }, []);

  useEffect(() => { load(); }, [load]);

  return (
    <div className="max-w-2xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-xl font-bold text-slate-800">📝 掲示板</h1>
        <button
          onClick={load}
          className="text-xs text-slate-400 hover:text-indigo-600 transition"
        >
          🔄 更新
        </button>
      </div>

      {loading ? (
        <p className="text-slate-400 text-sm">読み込み中...</p>
      ) : threads.length === 0 ? (
        <div className="text-center py-16 text-slate-400">
          <p className="text-3xl mb-3">💬</p>
          <p className="text-sm">まだコメントがありません。</p>
          <p className="text-xs mt-1">記事を読んで最初の投稿者になりましょう！</p>
        </div>
      ) : (
        <div className="space-y-2">
          {threads.map((t, i) => (
            <button
              key={t.slug}
              onClick={() => router.push(`/glossary/${t.slug}`)}
              className="w-full text-left border rounded-xl px-4 py-3 bg-white hover:border-indigo-300 hover:shadow-sm transition group"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex items-start gap-3 min-w-0">
                  <span className="text-slate-300 font-mono text-sm shrink-0 mt-0.5">
                    {String(i + 1).padStart(3, "0")}
                  </span>
                  <div className="min-w-0">
                    <p className="font-medium text-slate-800 truncate group-hover:text-indigo-600 transition">
                      {t.title}
                    </p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <span className="text-xs px-1.5 py-0.5 rounded-full bg-slate-100 text-slate-500">
                        {t.category}
                      </span>
                      <span className="text-xs text-slate-400">
                        最終: {formatDate(t.lastAt)}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 mt-1 truncate">
                      <span className="font-mono text-green-700">
                        ID:{t.comments[t.comments.length - 1].user_id}
                      </span>
                      {" "}
                      {t.comments[t.comments.length - 1].content}
                    </p>
                  </div>
                </div>
                <div className="shrink-0 flex flex-col items-end gap-1">
                  <span className="text-xs font-semibold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded-full">
                    {t.comments.length} 件
                  </span>
                </div>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
