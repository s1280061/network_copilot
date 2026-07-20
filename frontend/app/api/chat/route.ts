import { NextRequest, NextResponse } from "next/server";
import staticContent from "@/lib/static-content.json";

const SC: any = staticContent;

const SYSTEM_PROMPT = `あなたはADAS・SDV・車載ネットワーク専門の技術教師です。
Ethernet, TCP/IP, UDP, SOME/IP, CAN, AUTOSAR, ROS2 DDS, DoIP, UDS, LiDAR, カメラ, V2X などを扱います。
初心者から実務エンジニアまで分かりやすく、実務での利用例を重視して説明してください。

回答は必ず以下の5つのMarkdown見出しで日本語で構成してください:

## 一言説明
（1〜2文で簡潔に答える）

## 詳細解説
（技術的な詳細、仕組み、規格などを分かりやすく説明する）

## 自動運転での利用例
（ADAS・自動運転システムにおける具体的な使い方・事例を挙げる）

## 関連知識
（関連するプロトコル・規格・ツールを箇条書きで挙げる）

## 次に学ぶべきこと
（このトピックの次に学ぶと理解が深まるものを箇条書きで挙げる）`;

function stripHtml(html: string): string {
  return html.replace(/<[^>]+>/g, " ").replace(/\s+/g, " ").trim();
}

// Japanese question phrasings that carry no search signal ("〜とは？", "〜について"…).
// Stripped so the actual term remains for matching (Japanese has no word spaces,
// so "RAGとは" would otherwise become a single unmatchable token).
const QUESTION_STOPWORDS = [
  "とは何ですか", "とは何か", "とはなにか", "とは何", "とはなに", "とは",
  "について教えて", "についておしえて", "について", "を教えて", "を説明して",
  "を教えてください", "教えてください", "って何ですか", "ってなに", "って何",
  "ってなんですか", "の意味", "の仕組み", "の使い方", "どういう意味", "どういうもの",
  "ですか", "とはどういう", "を知りたい", "が知りたい", "説明して", "って", "とは?",
];

function normalizeQuestion(q: string): string {
  let s = q.toLowerCase();
  for (const w of QUESTION_STOPWORDS) s = s.split(w.toLowerCase()).join(" ");
  return s;
}

const SPLIT_RE = /[\s　、。.，,／\/・:：;；()（）「」『』【】\[\]?？!！]+/;

function ragSearch(question: string, k = 3): { slug: string; title: string; text: string }[] {
  const qLower = question.toLowerCase();
  const qNorm = normalizeQuestion(question);

  // query tokens: normalized chunks + standalone latin/number runs
  const chunkTokens = qNorm.split(SPLIT_RE).filter((w) => w.length > 1);
  const latinTokens = (qNorm.match(/[a-z0-9]+/g) || []).filter((w) => w.length > 1);
  const qTokens = Array.from(new Set([...chunkTokens, ...latinTokens]));

  const articles: any[] = SC.articles || [];
  const scored = articles.map((a: any) => {
    const title = (a.title || "").toLowerCase();
    const tags = (a.tags || []).map((t: any) => String(t).toLowerCase());
    // keyword pieces of the title (handles Japanese terms in parentheses etc.)
    const titleParts = title.split(SPLIT_RE).filter((w: string) => w.length > 1);
    const slugParts = String(a.slug || "").toLowerCase().split(/[-_]+/).filter((w) => w.length > 1);

    const hay = [title, a.excerpt || "", ...tags, a.category || ""].join(" ").toLowerCase();

    let score = 0;
    // forward: query token found in the article's text (title hits weigh more)
    for (const w of qTokens) {
      if (title.includes(w)) score += 3;
      else if (hay.includes(w)) score += 1;
    }
    // reverse: an article keyword appears in the question itself
    // (catches Japanese terms like "俯瞰変換" that don't tokenize on spaces)
    for (const t of tags) if (t.length > 1 && qLower.includes(t)) score += 2;
    for (const p of titleParts) if (qLower.includes(p)) score += 3;
    for (const p of slugParts) if (qLower.includes(p)) score += 2;
    // strong boost when the whole title is mentioned
    if (title.length > 1 && qLower.includes(title)) score += 5;

    return { slug: a.slug, title: a.title, score };
  });

  const top = scored
    .filter((x) => x.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, k);

  return top.map(({ slug, title }) => {
    const full = SC.bySlug?.[slug];
    const text = full?.html ? stripHtml(full.html).slice(0, 1200) : "";
    return { slug, title, text };
  });
}

export async function POST(req: NextRequest) {
  const { question } = await req.json();
  if (!question?.trim()) {
    return NextResponse.json({ error: "question required" }, { status: 400 });
  }

  const sources = ragSearch(question);

  const context =
    sources.length > 0
      ? "【参考記事】\n" +
        sources.map((s) => `■ ${s.title}\n${s.text}`).join("\n\n")
      : "";

  const userContent = context
    ? `${context}\n\n質問: ${question}`
    : `質問: ${question}`;

  const apiKey = process.env.GROQ_API_KEY;
  if (!apiKey) {
    return NextResponse.json(
      {
        answer:
          "## 一言説明\nAIチャットを使用するには Groq API キーの設定が必要です。\n\n## 詳細解説\nVercelの環境変数に `GROQ_API_KEY` を設定してください。Groq Cloud (console.groq.com) でAPIキーを発行できます。\n\n## 自動運転での利用例\nAPI設定後、ADAS・車載ネットワークについて何でも質問できます。\n\n## 関連知識\n- Groq Cloud API (OpenAI互換)\n- Vercel Environment Variables\n\n## 次に学ぶべきこと\n- API設定後にこの画面に戻ってください",
        sources: sources.map((s) => ({ slug: s.slug, title: s.title })),
      },
      { status: 200 }
    );
  }

  try {
    const resp = await fetch("https://api.groq.com/openai/v1/chat/completions", {
      method: "POST",
      headers: {
        "Authorization": `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        model: "llama-3.3-70b-versatile",
        max_tokens: 1500,
        messages: [
          { role: "system", content: SYSTEM_PROMPT },
          { role: "user", content: userContent },
        ],
      }),
    });

    if (!resp.ok) {
      throw new Error(`Groq API error: ${resp.status}`);
    }

    const data = await resp.json();
    const answer = data.choices?.[0]?.message?.content ?? "（回答を取得できませんでした）";

    return NextResponse.json({
      answer,
      sources: sources.map((s) => ({ slug: s.slug, title: s.title })),
    });
  } catch (err: any) {
    return NextResponse.json(
      {
        answer: `（Groq AI呼び出しに失敗しました: ${err.message}）`,
        sources: sources.map((s) => ({ slug: s.slug, title: s.title })),
      },
      { status: 200 }
    );
  }
}
