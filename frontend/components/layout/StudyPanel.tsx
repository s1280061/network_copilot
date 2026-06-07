"use client";

import Link from "next/link";
import { useStudyPanel } from "@/lib/study-context";

export default function StudyPanel() {
  const { panel } = useStudyPanel();
  const empty =
    !panel.prereq?.length &&
    !panel.related?.length &&
    !panel.next?.length &&
    !panel.recommendations?.length &&
    !panel.note;

  return (
    <aside className="w-72 shrink-0 border-l bg-white overflow-y-auto p-4 hidden lg:block">
      <h2 className="text-xs font-bold text-slate-400 uppercase tracking-wide mb-3">
        学習支援パネル
      </h2>

      {empty && (
        <p className="text-sm text-slate-400">
          記事やチャット、PCAP解析を開くと、関連用語や次に学ぶべき項目がここに表示されます。
        </p>
      )}

      {panel.note && (
        <div className="mb-4 rounded-lg bg-sky-50 border border-sky-200 p-3 text-sm text-sky-900">
          {panel.note}
        </div>
      )}

      <Section title="前提知識" items={panel.prereq} />
      <Section title="関連知識" items={panel.related} />
      <Section title="推奨記事" items={panel.recommendations} highlight />
      <Section title="次に学ぶべき項目" items={panel.next} highlight />
    </aside>
  );
}

function Section({
  title,
  items,
  highlight,
}: {
  title: string;
  items?: { slug: string; title: string }[];
  highlight?: boolean;
}) {
  if (!items?.length) return null;
  return (
    <div className="mb-5">
      <h3 className="text-sm font-semibold text-slate-700 mb-2">{title}</h3>
      <div className="flex flex-col gap-1.5">
        {items.map((it) => (
          <Link
            key={it.slug}
            href={`/glossary/${it.slug}`}
            className={`text-sm rounded-md px-2.5 py-1.5 transition-colors ${
              highlight
                ? "bg-sky-50 text-sky-700 hover:bg-sky-100"
                : "text-slate-600 hover:bg-slate-100"
            }`}
          >
            {it.title} →
          </Link>
        ))}
      </div>
    </div>
  );
}
