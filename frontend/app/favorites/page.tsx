"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getFavorites, removeFavorite } from "@/lib/api";
import { Ref } from "@/lib/types";

export default function FavoritesPage() {
  const [favs, setFavs] = useState<(Ref & { created_at: string })[]>([]);

  const load = () =>
    getFavorites().then((d) => setFavs(d.favorites)).catch(() => {});

  useEffect(() => {
    load();
  }, []);

  async function remove(slug: string) {
    await removeFavorite(slug);
    load();
  }

  return (
    <div>
      <header className="mb-5">
        <h1 className="text-2xl font-bold">⭐ お気に入り</h1>
        <p className="text-slate-500 text-sm mt-1">保存した記事の一覧です。</p>
      </header>

      {favs.length === 0 && (
        <p className="text-slate-400 text-sm">
          まだお気に入りはありません。記事ページの「☆ お気に入り」で保存できます。
        </p>
      )}

      <ul className="space-y-2">
        {favs.map((f) => (
          <li
            key={f.slug}
            className="flex items-center justify-between border rounded-lg p-3 bg-white"
          >
            <Link href={`/glossary/${f.slug}`} className="font-medium hover:text-sky-700">
              {f.title}
            </Link>
            <button
              onClick={() => remove(f.slug)}
              className="text-xs text-slate-400 hover:text-red-500"
            >
              削除
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}
