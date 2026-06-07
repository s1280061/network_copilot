"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getHistory } from "@/lib/api";
import { History } from "@/lib/types";

export default function HistoryPage() {
  const [h, setH] = useState<History | null>(null);

  useEffect(() => {
    getHistory().then(setH).catch(() => {});
  }, []);

  return (
    <div>
      <header className="mb-5">
        <h1 className="text-2xl font-bold">📝 学習履歴</h1>
        <p className="text-slate-500 text-sm mt-1">
          閲覧した記事・AIへの質問・PCAP解析の履歴です。
        </p>
      </header>

      {!h && <p className="text-slate-400">読み込み中...</p>}

      {h && (
        <div className="space-y-6">
          <Section title="閲覧した記事">
            {h.views.length === 0 && <Empty />}
            <ul className="space-y-1">
              {h.views.map((v) => (
                <li key={v.id} className="text-sm flex justify-between">
                  <Link
                    href={`/glossary/${v.slug}`}
                    className="hover:text-sky-700"
                  >
                    {v.title}
                  </Link>
                  <span className="text-slate-400">{v.viewed_at}</span>
                </li>
              ))}
            </ul>
          </Section>

          <Section title="AIへの質問">
            {h.chats.length === 0 && <Empty />}
            <ul className="space-y-1">
              {h.chats.map((c) => (
                <li key={c.id} className="text-sm flex justify-between gap-3">
                  <span className="truncate">{c.question}</span>
                  <span className="text-slate-400 shrink-0">{c.created_at}</span>
                </li>
              ))}
            </ul>
          </Section>

          <Section title="PCAP解析">
            {h.pcaps.length === 0 && <Empty />}
            <ul className="space-y-1">
              {h.pcaps.map((p) => (
                <li key={p.id} className="text-sm flex justify-between gap-3">
                  <span className="truncate font-mono">{p.filename}</span>
                  <span className="text-slate-400 shrink-0">{p.created_at}</span>
                </li>
              ))}
            </ul>
          </Section>
        </div>
      )}
    </div>
  );
}

function Section({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="border rounded-lg p-4 bg-white">
      <h2 className="font-semibold mb-2">{title}</h2>
      {children}
    </div>
  );
}

function Empty() {
  return <p className="text-sm text-slate-400">履歴はありません。</p>;
}
