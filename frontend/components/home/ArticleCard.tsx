"use client";

import Link from "next/link";
import { ArticleMeta } from "@/lib/types";
import Thumbnail, { categoryStyle } from "@/components/Thumbnail";

export default function ArticleCard({ a }: { a: ArticleMeta }) {
  const style = categoryStyle(a.category);

  return (
    <Link
      href={`/glossary/${a.slug}`}
      className="block w-full sm:w-56 sm:shrink-0 border rounded-xl bg-white overflow-hidden hover:border-sky-400 hover:shadow-md transition"
    >
      <Thumbnail slug={a.slug} category={a.category} className="h-28 w-full" />
      <div className="p-3">
        <span className={`text-xs px-2 py-0.5 rounded-full ${style.bg} ${style.text}`}>
          {a.category}
        </span>
        <h3 className="font-semibold text-sm leading-snug line-clamp-2 mt-2">{a.title}</h3>
        <p className="text-xs text-slate-500 mt-1 line-clamp-2">{a.excerpt}</p>
      </div>
    </Link>
  );
}
