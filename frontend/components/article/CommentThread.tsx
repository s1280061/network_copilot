"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { getComments, postComment, Comment, IS_STATIC } from "@/lib/api";

/** ブラウザに保存する匿名ID（日付ベース、毎日変わる2ch風） */
function getAnonymousId(): string {
  const stored = localStorage.getItem("nc_user_id");
  if (stored) return stored;
  // 8文字のランダム英数字
  const id = Math.random().toString(36).slice(2, 10).toUpperCase();
  localStorage.setItem("nc_user_id", id);
  return id;
}

function formatDate(s: string) {
  const d = new Date(s);
  return `${d.getFullYear()}/${String(d.getMonth() + 1).padStart(2, "0")}/${String(d.getDate()).padStart(2, "0")} ${String(d.getHours()).padStart(2, "0")}:${String(d.getMinutes()).padStart(2, "0")}:${String(d.getSeconds()).padStart(2, "0")}`;
}

export default function CommentThread({ slug }: { slug: string }) {
  const [comments, setComments] = useState<Comment[]>([]);
  const [content, setContent] = useState("");
  const [userId, setUserId] = useState("");
  const [posting, setPosting] = useState(false);
  const [error, setError] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  const load = useCallback(async () => {
    const c = await getComments(slug);
    setComments(c);
  }, [slug]);

  useEffect(() => {
    setUserId(getAnonymousId());
    load();
  }, [load]);

  async function handlePost(e: React.FormEvent) {
    e.preventDefault();
    if (!content.trim() || posting) return;
    setPosting(true);
    setError("");
    const result = await postComment(slug, userId, content.trim());
    if (result) {
      setComments((prev) => [...prev, result]);
      setContent("");
      setTimeout(() => bottomRef.current?.scrollIntoView({ behavior: "smooth" }), 50);
    } else {
      setError("投稿に失敗しました。バックエンドが必要です。");
    }
    setPosting(false);
  }

  if (IS_STATIC) {
    return (
      <div className="mt-10 pt-6 border-t border-slate-200">
        <p className="text-xs text-slate-400 text-center">
          💬 コメント機能はバックエンド接続時のみ利用できます
        </p>
      </div>
    );
  }

  return (
    <div className="mt-10 pt-6 border-t border-slate-200">
      {/* ヘッダー */}
      <div className="flex items-center gap-2 mb-4">
        <span className="text-sm font-semibold text-slate-700">💬 質問・コメント</span>
        <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-500">
          {comments.length} 件
        </span>
      </div>

      {/* スレッド本文（2ch風） */}
      <div className="bg-slate-50 rounded-lg border border-slate-200 divide-y divide-slate-100 max-h-96 overflow-y-auto text-sm">
        {comments.length === 0 ? (
          <p className="text-slate-400 text-xs text-center py-8">
            まだコメントがありません。最初の投稿者になりましょう！
          </p>
        ) : (
          comments.map((c, i) => (
            <div key={c.id} className="px-3 py-2.5 hover:bg-white transition">
              <div className="flex items-baseline gap-2 mb-1">
                <span className="text-slate-400 text-xs font-mono">{i + 1}</span>
                <span className="font-mono text-xs font-semibold text-green-700 bg-green-50 px-1.5 py-0.5 rounded">
                  ID:{c.user_id}
                </span>
                <span className="text-slate-400 text-xs">{formatDate(c.created_at)}</span>
              </div>
              <p className="text-slate-700 leading-relaxed whitespace-pre-wrap break-words pl-6">
                {c.content}
              </p>
            </div>
          ))
        )}
        <div ref={bottomRef} />
      </div>

      {/* 投稿フォーム */}
      <form onSubmit={handlePost} className="mt-3 space-y-2">
        <div className="flex items-center gap-2 text-xs text-slate-500">
          <span>あなたのID：</span>
          <span className="font-mono font-semibold text-green-700 bg-green-50 px-2 py-0.5 rounded">
            {userId}
          </span>
          <span className="text-slate-300">（匿名・自動発行）</span>
        </div>
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="質問・感想・補足など（最大1000文字）"
          rows={3}
          maxLength={1000}
          className="w-full text-sm border border-slate-300 rounded-lg px-3 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-indigo-400 focus:border-transparent"
        />
        {error && <p className="text-xs text-red-500">{error}</p>}
        <div className="flex justify-between items-center">
          <span className="text-xs text-slate-400">{content.length} / 1000</span>
          <button
            type="submit"
            disabled={posting || !content.trim()}
            className="text-sm px-4 py-1.5 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition"
          >
            {posting ? "投稿中..." : "書き込む"}
          </button>
        </div>
      </form>
    </div>
  );
}
