"use client";

import Link from "next/link";
import { ArticleMeta } from "@/lib/types";

const CATEGORY_STYLE: Record<
  string,
  { bg: string; text: string; icon: string }
> = {
  Ethernet:  { bg: "bg-blue-100",   text: "text-blue-700",   icon: "🔌" },
  "TCP/IP":  { bg: "bg-sky-100",    text: "text-sky-700",    icon: "🌐" },
  PCAP:      { bg: "bg-violet-100", text: "text-violet-700", icon: "🔍" },
  "SOME/IP": { bg: "bg-orange-100", text: "text-orange-700", icon: "🚗" },
  AUTOSAR:   { bg: "bg-green-100",  text: "text-green-700",  icon: "⚙️" },
  SDV:       { bg: "bg-rose-100",   text: "text-rose-700",   icon: "🤖" },
};

const DEFAULT_STYLE = { bg: "bg-slate-100", text: "text-slate-600", icon: "📄" };

export default function ArticleCard({ a }: { a: ArticleMeta }) {
  const style = CATEGORY_STYLE[a.category] ?? DEFAULT_STYLE;

  return (
    <Link
      href={`/glossary/${a.slug}`}
      className="block w-64 shrink-0 border rounded-xl bg-white overflow-hidden hover:border-sky-400 hover:shadow-md transition"
    >
      {/* thumbnail banner */}
      <div className={`${style.bg} flex items-center justify-center h-24`}>
        <span className="text-4xl">{style.icon}</span>
      </div>

      <div className="p-4">
        <div className="flex items-center gap-2 mb-2">
          <span className={`text-xs px-2 py-0.5 rounded-full ${style.bg} ${style.text}`}>
            {a.category}
          </span>
          {a.completed && <span className="text-xs text-green-600">✓</span>}
          {a.favorite && <span className="text-xs text-amber-500">★</span>}
        </div>
        <h3 className="font-semibold leading-snug line-clamp-2">{a.title}</h3>
        <p className="text-sm text-slate-500 mt-1 line-clamp-2 min-h-[2.5rem]">
          {a.excerpt}
        </p>
        <div className="flex items-center justify-between text-xs text-slate-400 mt-3">
          <span>👁 {a.views ?? 0}</span>
          <span>{a.updated}</span>
        </div>
      </div>
    </Link>
  );
}
