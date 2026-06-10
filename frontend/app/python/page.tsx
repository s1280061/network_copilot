"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { getArticles } from "@/lib/api";
import { ArticleMeta } from "@/lib/types";
import Thumbnail from "@/components/Thumbnail";

const PYTHON_SLUGS = [
  "python-basics",
  "numpy",
  "pandas",
  "matplotlib",
  "seaborn",
  "data-cleaning",
  "data-analysis",
];

const SECTION_ORDER = [
  { label: "入門", slugs: ["python-basics"] },
  { label: "数値・データ操作", slugs: ["numpy", "pandas", "data-cleaning"] },
  { label: "可視化", slugs: ["matplotlib", "seaborn"] },
  { label: "分析", slugs: ["data-analysis"] },
];

export default function PythonPage() {
  const [articles, setArticles] = useState<Record<string, ArticleMeta>>({});

  useEffect(() => {
    getArticles()
      .then((d) => {
        const map: Record<string, ArticleMeta> = {};
        for (const a of d.articles) {
          if (PYTHON_SLUGS.includes(a.slug)) map[a.slug] = a;
        }
        setArticles(map);
      })
      .catch(() => {});
  }, []);

  return (
    <div className="space-y-10">
      <header>
        <div className="flex items-center gap-3 mb-1">
          <span className="text-3xl">🐍</span>
          <h1 className="text-2xl font-bold">Pythonデータサイエンス</h1>
        </div>
        <p className="text-slate-500 text-sm">
          NumPy・Pandas・Matplotlib・Seaborn など、データ分析に使うPythonライブラリをコード例とともに学べます。
        </p>
      </header>

      {/* learning path */}
      <section>
        <h2 className="font-bold text-slate-700 mb-3">学習の流れ</h2>
        <div className="flex items-center gap-2 flex-wrap text-sm">
          {PYTHON_SLUGS.map((slug, i) => (
            <span key={slug} className="flex items-center gap-2">
              <Link
                href={`/glossary/${slug}`}
                className="px-3 py-1 rounded-full bg-yellow-100 text-yellow-800 hover:bg-yellow-200 transition"
              >
                {articles[slug]?.title ?? slug}
              </Link>
              {i < PYTHON_SLUGS.length - 1 && (
                <span className="text-slate-300">→</span>
              )}
            </span>
          ))}
        </div>
      </section>

      {/* sections */}
      {SECTION_ORDER.map((section) => (
        <section key={section.label}>
          <h2 className="font-bold mb-4 text-lg border-b pb-1">{section.label}</h2>
          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {section.slugs.map((slug) => {
              const a = articles[slug];
              if (!a) return null;
              return (
                <Link
                  key={slug}
                  href={`/glossary/${slug}`}
                  className="block border rounded-xl bg-white overflow-hidden hover:border-yellow-400 hover:shadow-md transition"
                >
                  <Thumbnail
                    slug={a.slug}
                    category={a.category}
                    className="h-32 w-full"
                    iconClassName="text-4xl"
                  />
                  <div className="p-4">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="text-xs px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-800">
                        Level {a.level}
                      </span>
                      {a.completed && (
                        <span className="text-xs text-green-600">✓ 学習済み</span>
                      )}
                    </div>
                    <h3 className="font-semibold leading-snug">{a.title}</h3>
                    <p className="text-sm text-slate-500 mt-1 line-clamp-2">
                      {a.excerpt}
                    </p>
                  </div>
                </Link>
              );
            })}
          </div>
        </section>
      ))}

      {Object.keys(articles).length === 0 && (
        <p className="text-slate-400 text-sm">読み込み中...</p>
      )}
    </div>
  );
}
