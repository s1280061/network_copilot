"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { uploadPcap } from "@/lib/api";
import { PcapResult } from "@/lib/types";
import { useStudyPanel } from "@/lib/study-context";
import Mermaid from "@/components/Mermaid";

export default function PcapPage() {
  const router = useRouter();
  const { setPanel } = useStudyPanel();
  const [result, setResult] = useState<PcapResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState("");

  async function onFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    setErr("");
    try {
      const r = await uploadPcap(file);
      setResult(r);
      setPanel({
        title: "PCAP解析",
        note: r.recommend_note,
        recommendations: r.recommendations,
      });
    } catch {
      setErr("解析に失敗しました。.pcap / .pcapng ファイルか確認してください。");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <header className="mb-4">
        <h1 className="text-2xl font-bold">PCAP解析</h1>
        <p className="text-slate-500 text-sm mt-1">
          キャプチャをアップロードすると、プロトコル構成を解析し、関連する学習記事を推薦します。
        </p>
      </header>

      <input
        type="file"
        accept=".pcap,.pcapng,.cap"
        onChange={onFile}
        className="mb-4 block"
      />
      {loading && <p className="text-slate-400 text-sm">解析中...</p>}
      {err && <p className="text-red-600 text-sm">{err}</p>}

      {result && (
        <div className="space-y-5">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            <Stat label="パケット数" value={result.packet_count} />
            <Stat
              label="プロトコル種類"
              value={Object.keys(result.protocols).length}
            />
            <Stat label="通信相手" value={result.peers.length} />
            <Stat label="ポート" value={result.ports.length} />
          </div>

          {result.recommendations.length > 0 && (
            <div className="rounded-lg bg-sky-50 border border-sky-200 p-4">
              <p className="text-sm text-sky-900 mb-2">{result.recommend_note}</p>
              <p className="text-xs text-slate-500 mb-2">おすすめ記事:</p>
              <div className="flex flex-wrap gap-2">
                {result.recommendations.map((r) => (
                  <button
                    key={r.slug}
                    onClick={() => router.push(`/glossary/${r.slug}`)}
                    className="text-sm bg-white border border-sky-300 text-sky-700 rounded px-3 py-1 hover:bg-sky-100"
                  >
                    {r.title} →
                  </button>
                ))}
              </div>
            </div>
          )}

          <Card title="プロトコル一覧">
            <div className="flex flex-wrap gap-2">
              {Object.entries(result.protocols).map(([k, v]) => (
                <span
                  key={k}
                  className="bg-slate-100 text-slate-700 px-2 py-1 rounded text-sm"
                >
                  {k}: {v}
                </span>
              ))}
            </div>
          </Card>

          <div className="grid md:grid-cols-2 gap-4">
            <Card title="通信相手一覧">
              <ul className="text-sm space-y-1">
                {result.peers.map((p) => (
                  <li key={p.address} className="flex justify-between">
                    <span className="font-mono">{p.address}</span>
                    <span className="text-slate-400">{p.count}</span>
                  </li>
                ))}
              </ul>
            </Card>
            <Card title="ポート一覧">
              <ul className="text-sm space-y-1">
                {result.ports.map((p) => (
                  <li key={p.port} className="flex justify-between">
                    <span className="font-mono">{p.port}</span>
                    <span className="text-slate-400">{p.count}</span>
                  </li>
                ))}
              </ul>
            </Card>
          </div>

          <Card title="プロトコルスタック (階層構造)">
            <Mermaid chart={result.mermaid} />
          </Card>

          <Card title="🤖 学習支援モード (AI解説)">
            <p className="whitespace-pre-wrap text-sm">{result.explanation}</p>
          </Card>
        </div>
      )}
    </div>
  );
}

function Stat({ label, value }: { label: string; value: number }) {
  return (
    <div className="bg-white border rounded-lg p-3 text-center">
      <p className="text-2xl font-bold text-sky-700">{value}</p>
      <p className="text-xs text-slate-500">{label}</p>
    </div>
  );
}

function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="border rounded-lg p-4 bg-white">
      <h3 className="font-semibold mb-2">{title}</h3>
      {children}
    </div>
  );
}
