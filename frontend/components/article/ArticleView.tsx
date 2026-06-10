"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import mermaid from "mermaid";
import hljs from "highlight.js/lib/core";
import python from "highlight.js/lib/languages/python";
import bash from "highlight.js/lib/languages/bash";
import javascript from "highlight.js/lib/languages/javascript";
import typescript from "highlight.js/lib/languages/typescript";
import json from "highlight.js/lib/languages/json";
import yaml from "highlight.js/lib/languages/yaml";
import sql from "highlight.js/lib/languages/sql";
import cpp from "highlight.js/lib/languages/cpp";
import { getArticle, getRecommend } from "@/lib/api";
import { Article, Ref } from "@/lib/types";
import { useStudyPanel } from "@/lib/study-context";
import Thumbnail from "@/components/Thumbnail";

hljs.registerLanguage("python", python);
hljs.registerLanguage("bash", bash);
hljs.registerLanguage("shell", bash);
hljs.registerLanguage("javascript", javascript);
hljs.registerLanguage("typescript", typescript);
hljs.registerLanguage("json", json);
hljs.registerLanguage("yaml", yaml);
hljs.registerLanguage("sql", sql);
hljs.registerLanguage("cpp", cpp);
hljs.registerLanguage("c", cpp);

mermaid.initialize({ startOnLoad: false, theme: "default", securityLevel: "loose" });

/** language-xxx クラスから言語名を抽出 */
function getLang(code: HTMLElement): string {
  const cls = Array.from(code.classList).find((c) => c.startsWith("language-"));
  return cls ? cls.replace("language-", "") : "";
}

/** コピーボタンを生成 */
function makeCopyBtn(text: string): HTMLButtonElement {
  const btn = document.createElement("button");
  btn.className = "hljs-copy-btn";
  btn.textContent = "コピー";
  btn.addEventListener("click", () => {
    navigator.clipboard.writeText(text).then(() => {
      btn.textContent = "✓ コピー済み";
      setTimeout(() => { btn.textContent = "コピー"; }, 2000);
    });
  });
  return btn;
}

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
        setPanel({
          slug: a.slug,
          related: [...a.related_full, ...a.next_full],
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

  // Mermaid rendering
  useEffect(() => {
    if (!article) return;
    const blocks = document.querySelectorAll<HTMLElement>(
      ".prose-article code.language-mermaid"
    );
    blocks.forEach(async (block, i) => {
      const chart = block.textContent || "";
      const id = `mermaid-${slug}-${i}`;
      try {
        const { svg } = await mermaid.render(id, chart);
        const wrapper = document.createElement("div");
        wrapper.className = "overflow-x-auto my-6 flex justify-center";
        wrapper.innerHTML = svg;
        block.closest("pre")?.replaceWith(wrapper);
      } catch {
        // leave as-is on error
      }
    });
  }, [article, slug]);

  // Syntax highlighting
  useEffect(() => {
    if (!article) return;
    const codeBlocks = document.querySelectorAll<HTMLElement>(".prose-article pre code");
    codeBlocks.forEach((code) => {
      const lang = getLang(code);
      if (lang === "mermaid") return;

      // ハイライト実行
      if (lang && hljs.getLanguage(lang)) {
        code.innerHTML = hljs.highlight(code.textContent || "", { language: lang }).value;
      } else {
        hljs.highlightElement(code);
      }
      code.classList.add("hljs");

      // pre ラッパーをスタイリング済みにする
      const pre = code.closest("pre");
      if (!pre || pre.classList.contains("hljs-wrapped")) return;
      pre.classList.add("hljs-wrapped");

      // 言語バッジ
      if (lang && lang !== "text") {
        const badge = document.createElement("span");
        badge.className = "hljs-lang-badge";
        badge.textContent = lang;
        pre.appendChild(badge);
      }

      // コピーボタン
      const btn = makeCopyBtn(code.textContent || "");
      pre.appendChild(btn);
    });
  }, [article, slug]);

  // SPA link interception
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

  if (error)
    return <p className="text-red-600">記事が見つかりませんでした: {slug}</p>;
  if (!article) return <p className="text-slate-400">読み込み中...</p>;

  const allRelated = [
    ...article.related_full,
    ...article.next_full,
    ...article.prereq_full,
  ].filter((r, i, arr) => arr.findIndex((x) => x.slug === r.slug) === i);

  return (
    <article>
      <Thumbnail
        slug={article.slug}
        category={article.category}
        className="w-full h-48 sm:h-64 rounded-xl mb-6"
        iconClassName="text-6xl"
      />

      <div className="mb-6">
        <span className="text-xs px-2 py-0.5 rounded-full bg-slate-100 text-slate-500">
          {article.category}
        </span>
        <h1 className="text-2xl font-bold mt-2">{article.title}</h1>
        <p className="text-xs text-slate-400 mt-1">{article.updated}</p>
      </div>

      <div
        className="prose-article"
        dangerouslySetInnerHTML={{ __html: article.html }}
      />

      {allRelated.length > 0 && (
        <div className="mt-10 pt-6 border-t">
          <p className="text-sm font-semibold text-slate-600 mb-3">関連記事</p>
          <div className="flex flex-wrap gap-2">
            {allRelated.map((it) => (
              <button
                key={it.slug}
                onClick={() => router.push(`/glossary/${it.slug}`)}
                className="text-sm border rounded-full px-4 py-1.5 bg-white text-slate-700 hover:border-sky-400 hover:text-sky-600 transition"
              >
                {it.title}
              </button>
            ))}
          </div>
        </div>
      )}

      {recommended.length > 0 && (
        <div className="mt-8">
          <p className="text-sm font-semibold text-slate-600 mb-3">おすすめ記事</p>
          <div className="grid sm:grid-cols-2 gap-2">
            {recommended.map((r) => (
              <button
                key={r.slug}
                onClick={() => router.push(`/glossary/${r.slug}`)}
                className="text-left text-sm border rounded-lg px-4 py-3 bg-white hover:border-sky-400 hover:shadow-sm transition"
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
