"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { chat } from "@/lib/api";
import { Ref } from "@/lib/types";
import { useStudyPanel } from "@/lib/study-context";

type Msg = { role: "user" | "ai"; text: string; sources?: Ref[] };

export default function ChatPage() {
  const router = useRouter();
  const { setPanel } = useStudyPanel();
  const [msgs, setMsgs] = useState<Msg[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function send() {
    if (!input.trim() || loading) return;
    const q = input;
    setMsgs((m) => [...m, { role: "user", text: q }]);
    setInput("");
    setLoading(true);
    try {
      const { answer, sources } = await chat(q);
      setMsgs((m) => [...m, { role: "ai", text: answer, sources }]);
      setPanel({ title: "チャット", recommendations: sources });
    } catch {
      setMsgs((m) => [
        ...m,
        { role: "ai", text: "エラー: バックエンドに接続できません。" },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <header className="mb-4">
        <h1 className="text-2xl font-bold">AIチャット</h1>
        <p className="text-slate-500 text-sm mt-1">
          回答は「一言説明 / 詳細解説 / 自動運転での利用例 / 関連知識 / 次に学ぶべきこと」で構成され、関連記事(RAG)を参考に回答します。
        </p>
      </header>

      <div className="space-y-3 mb-4 min-h-[240px]">
        {msgs.length === 0 && (
          <p className="text-slate-400 text-sm">
            例: 「UDPとTCPの違いは?」「SOME/IPとは?」「OSI参照モデルとは?」
          </p>
        )}
        {msgs.map((m, i) => (
          <div
            key={i}
            className={`rounded-lg p-3 text-sm whitespace-pre-wrap ${
              m.role === "user"
                ? "bg-sky-50 border border-sky-200"
                : "bg-white border border-slate-200"
            }`}
          >
            <span className="font-semibold mr-2">
              {m.role === "user" ? "🙋 あなた" : "🤖 Copilot"}
            </span>
            {m.text}
            {m.role === "ai" && m.sources && m.sources.length > 0 && (
              <div className="mt-3 pt-2 border-t flex flex-wrap gap-2">
                <span className="text-xs text-slate-400 w-full">📚 参考記事:</span>
                {m.sources.map((r) => (
                  <button
                    key={r.slug}
                    onClick={() => router.push(`/glossary/${r.slug}`)}
                    className="text-xs bg-sky-100 text-sky-700 rounded px-2 py-1 hover:bg-sky-200"
                  >
                    {r.title} →
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
        {loading && <p className="text-slate-400 text-sm">考え中...</p>}
      </div>

      <div className="flex gap-2 sticky bottom-0 bg-slate-50 py-2">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && send()}
          placeholder="ネットワークについて質問する..."
          className="flex-1 border rounded-lg px-4 py-2"
        />
        <button
          onClick={send}
          disabled={loading}
          className="bg-sky-600 text-white px-5 rounded-lg disabled:opacity-50"
        >
          送信
        </button>
      </div>
    </div>
  );
}
