import {
  Article,
  Roadmap,
  PcapResult,
  History,
  Ref,
  Home,
  Dashboard,
  SearchHit,
} from "./types";
import staticContent from "./static-content.json";

// When NEXT_PUBLIC_API_BASE is empty (e.g. Vercel-only "read" deployment),
// the app runs in STATIC MODE: articles are read from the bundled JSON and
// interactive features (AI chat, PCAP, progress save) are gracefully disabled.
const BASE = process.env.NEXT_PUBLIC_API_BASE || "";
const HAS_BACKEND = BASE !== "";

const SC: any = staticContent;

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) throw new Error(`${res.url} -> ${res.status}`);
  return res.json() as Promise<T>;
}

// Try the live API; fall back to a static value if backend is absent or errors.
async function liveOrStatic<T>(
  path: string,
  fallback: () => T,
  init?: RequestInit
): Promise<T> {
  if (!HAS_BACKEND) return fallback();
  try {
    const res = await fetch(`${BASE}${path}`, { cache: "no-store", ...init });
    return await json<T>(res);
  } catch {
    return fallback();
  }
}

// ---- content (read-only: works in static mode) ----
export const getRoadmap = () =>
  liveOrStatic<Roadmap>("/api/roadmap", () => SC.roadmap);

export const getArticles = () =>
  liveOrStatic<{ articles: Article[] }>("/api/articles", () => ({
    articles: SC.articles,
  }));

export const getArticle = (slug: string) =>
  liveOrStatic<Article>(`/api/articles/${slug}`, () => {
    const a = SC.bySlug[slug];
    if (!a) throw new Error("not found");
    return a;
  });

export const getHome = () =>
  liveOrStatic<Home>("/api/home", () => SC.home);

export const getDashboard = () =>
  liveOrStatic<Dashboard>("/api/dashboard", () => staticDashboard());

export const getRecommend = (slug: string) =>
  liveOrStatic<{ recommendations: Ref[] }>(
    `/api/articles/${slug}/recommend`,
    () => ({ recommendations: SC.recommend[slug] || [] })
  );

export const search = (q: string) =>
  liveOrStatic<{ results: SearchHit[]; mode: string }>(
    `/api/search?q=${encodeURIComponent(q)}`,
    () => ({ results: staticSearch(q), mode: "keyword" })
  );

// ---- interactive (need backend) ----
export const chat = (question: string) => {
  // Always use the Next.js API route (/api/chat) which works on Vercel.
  // Falls back to the Python backend if NEXT_PUBLIC_API_BASE is set.
  const chatUrl = HAS_BACKEND ? `${BASE}/api/chat` : "/api/chat";
  return fetch(chatUrl, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  }).then(json<{ answer: string; sources: Ref[] }>);
};

export const uploadPcap = (file: File) => {
  if (!HAS_BACKEND) {
    return Promise.reject(new Error("PCAP解析はバックエンド接続時のみ利用できます。"));
  }
  const form = new FormData();
  form.append("file", file);
  return fetch(`${BASE}/api/pcap`, { method: "POST", body: form }).then(
    json<PcapResult>
  );
};

// ---- progress / favorites (no-op in static mode) ----
export const setProgress = (slug: string, completed: boolean) =>
  liveOrStatic<{ ok: boolean }>(
    "/api/progress",
    () => ({ ok: false }),
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ slug, completed }),
    }
  );

export const addFavorite = (slug: string, title: string) =>
  liveOrStatic<{ ok: boolean }>(
    "/api/favorites",
    () => ({ ok: false }),
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ slug, title }),
    }
  );

export const removeFavorite = (slug: string) =>
  liveOrStatic<{ ok: boolean }>(`/api/favorites/${slug}`, () => ({ ok: false }), {
    method: "DELETE",
  });

export const getFavorites = () =>
  liveOrStatic<{ favorites: (Ref & { created_at: string })[] }>(
    "/api/favorites",
    () => ({ favorites: [] })
  );

export const getHistory = () =>
  liveOrStatic<History>("/api/history", () => ({
    views: [],
    chats: [],
    pcaps: [],
  }));

// ---- static helpers ----
function staticSearch(q: string): SearchHit[] {
  const s = q.trim().toLowerCase();
  if (!s) return [];
  return (SC.articles as Article[])
    .filter(
      (a) =>
        a.title.toLowerCase().includes(s) ||
        (a.excerpt || "").toLowerCase().includes(s) ||
        a.tags.some((t) => t.includes(s))
    )
    .slice(0, 8)
    .map((a) => ({ slug: a.slug, title: a.title, category: a.category }));
}

function staticDashboard(): Dashboard {
  const arts = SC.articles as Article[];
  const byCat: Record<string, { category: string; total: number; completed: number; rate: number }> = {};
  for (const a of arts) {
    byCat[a.category] = byCat[a.category] || {
      category: a.category,
      total: 0,
      completed: 0,
      rate: 0,
    };
    byCat[a.category].total += 1;
  }
  return {
    total: arts.length,
    completed: 0,
    rate: 0,
    categories: Object.values(byCat),
  };
}

export const IS_STATIC = !HAS_BACKEND;
