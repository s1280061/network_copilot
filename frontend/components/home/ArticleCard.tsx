"use client";

import Link from "next/link";
import { ArticleMeta } from "@/lib/types";
import Thumbnail, { categoryStyle } from "@/components/Thumbnail";

export default function ArticleCard({ a }: { a: ArticleMeta }) {
  const style = categoryStyle(a.category);

  return (
    <Link
      href={`/glossary/${a.slug}`}
      className="block w-64 shrink-0 border rounded-xl bg-white overflow-hidden hover:border-sky-400 hover:shadow-md transition"
    >
      {/* thumbnail (image if present, else colored banner) */}
      <Thumbnail slug={a.slug} category={a.category} className="h-24 w-full" />

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
