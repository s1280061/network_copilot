"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import {
  getArticle,
  setProgress,
  addFavorite,
  removeFavorite,
  getRecommend,
} from "@/lib/api";
import { Article, Ref } from "@/lib/types";
import { useStudyPanel } from "@/lib/study-context";
import { recordView } from "@/lib/profile";

export default function ArticleView({ slug }: { slug: string }) {
  const router = useRouter();
  const { setPanel } = useStudyPanel();
  const [article, setArticle] = useState<Article | null>(null);
  const [recommended, setRecommended] = useState<Ref[]>([]);
  const [error, setError] = useState(false);

  const load = useCallback(() => {
    setArticle(null);
    setRecommended([]);
    setError(false);
    getArticle(slug)
      .then((a) => {
        setArticle(a);
        recordView(a.slug);
        setPanel({
          title: a.title,
          slug: a.slug,
          prereq: a.prereq_full,
          related: a.related_full,
          next: a.next_full,
        });
      })
      .catch(() => setError(true));
    getRecommend(slug)
      .then((d) => setRecommended(d.recommendations))
      .catch(() => {});
  }, [slug, setPanel]);

  useEffect(() => {
    load();
  }, [load]);

  // Intercept internal [[term]] links for SPA navigation.
  useEffect(() => {
    function onClick(e: MouseEvent) {
      const t = (e.target as HTMLElement)?.closest("a.term-link");
      if (t) {
        e.preventDefault();
        const s = t.getAttribute("data-slug");
        if (s) router.push(`/glossary/${s}`);
      }
    }
    document.addEventListener("click", onClick);
    return () => document.removeEventListener("click", onClick);
  }, [router]);

  async function toggleDone() {
    if (!article) return;
    await setProgress(article.slug, !article.completed);
    setArticle({ ...article, completed: !article.completed });
  }

  async function toggleFav() {
    if (!article) return;
    if (article.favorite) await removeFavorite(article.slug);
    else await addFavorite(article.slug, article.title);
    setArticle({ ...article, favorite: !article.favorite });
  }

  if (error)
    return <p className="text-red-600">記事が見つかりませんでした: {slug}</p>;
  if (!article) return <p className="text-slate-400">読み込み中...</p>;

  return (
    <article>
      <div className="relative w-full h-52 rounded-xl overflow-hidden bg-slate-100 mb-6">
        <Image
          src={`/thumbnails/${article.slug}.jpg`}
          alt={article.title}
          fill
          className="object-cover"
          onError={(e) => { (e.currentTarget as HTMLImageElement).parentElement!.style.display = "none"; }}
        />
      </div>
      <div className="flex items-start justify-between gap-4 mb-4">
        <div>
          <span className="text-xs font-semibold text-sky-600">
            Level {article.level}
          </span>
          <h1 className="text-2xl font-bold">{article.title}</h1>
        </div>
        <div className="flex gap-2 shrink-0">
          <button
            onClick={toggleFav}
            className={`text-sm rounded-md px-3 py-1.5 border ${
              article.favorite
                ? "bg-amber-50 border-amber-300 text-amber-700"
                : "border-slate-300 text-slate-600 hover:bg-slate-50"
            }`}
          >
            {article.favorite ? "★ お気に入り" : "☆ お気に入り"}
          </button>
          <button
            onClick={toggleDone}
            className={`text-sm rounded-md px-3 py-1.5 border ${
              article.completed
                ? "bg-green-50 border-green-300 text-green-700"
                : "border-slate-300 text-slate-600 hover:bg-slate-50"
            }`}
          >
            {article.completed ? "✓ 学習済み" : "学習済みにする"}
          </button>
        </div>
      </div>

      <div
        className="prose-article"
        dangerouslySetInnerHTML={{ __html: article.html }}
      />

      {article.prereq_full.length > 0 && (
        <LinkSection
          label="前提知識"
          items={article.prereq_full}
          onClick={(s) => router.push(`/glossary/${s}`)}
        />
      )}

      {article.related_full.length > 0 && (
        <LinkSection
          label="関連知識"
          items={article.related_full}
          onClick={(s) => router.push(`/glossary/${s}`)}
        />
      )}

      {article.next_full.length > 0 && (
        <div className="mt-6 border-t pt-4">
          <p className="text-sm text-slate-500 mb-2">次に学ぶべき内容</p>
          <div className="flex flex-wrap gap-2">
            {article.next_full.map((n) => (
              <button
                key={n.slug}
                onClick={() => router.push(`/glossary/${n.slug}`)}
                className="text-sm bg-sky-600 text-white rounded-md px-3 py-1.5 hover:bg-sky-700"
              >
                {n.title} →
              </button>
            ))}
          </div>
        </div>
      )}

      {recommended.length > 0 && (
        <div className="mt-8 border-t pt-4">
          <p className="text-sm font-semibold text-slate-700 mb-2">
            ✨ あなたへのおすすめ
          </p>
          <div className="grid sm:grid-cols-2 gap-2">
            {recommended.map((r) => (
              <button
                key={r.slug}
                onClick={() => router.push(`/glossary/${r.slug}`)}
                className="text-left text-sm border rounded-lg px-3 py-2 bg-white hover:border-sky-400"
              >
                {r.title} →
              </button>
            ))}
          </div>
        </div>
      )}
    </article>
  );
}

function LinkSection({
  label,
  items,
  onClick,
}: {
  label: string;
  items: Ref[];
  onClick: (slug: string) => void;
}) {
  return (
    <div className="mt-6 border-t pt-4">
      <p className="text-sm text-slate-500 mb-2">{label}</p>
      <div className="flex flex-wrap gap-2">
        {items.map((it) => (
          <button
            key={it.slug}
            onClick={() => onClick(it.slug)}
            className="text-sm border rounded-md px-3 py-1.5 bg-white text-slate-700 hover:border-sky-400"
          >
            {it.title}
          </button>
        ))}
      </div>
    </div>
  );
}
