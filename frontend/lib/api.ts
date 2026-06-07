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

const BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8080";

async function json<T>(res: Response): Promise<T> {
  if (!res.ok) throw new Error(`${res.url} -> ${res.status}`);
  return res.json() as Promise<T>;
}

// ---- content ----
export const getRoadmap = () =>
  fetch(`${BASE}/api/roadmap`, { cache: "no-store" }).then(json<Roadmap>);

export const getArticles = () =>
  fetch(`${BASE}/api/articles`, { cache: "no-store" }).then(
    json<{ articles: Article[] }>
  );

export const getArticle = (slug: string) =>
  fetch(`${BASE}/api/articles/${slug}`, { cache: "no-store" }).then(
    json<Article>
  );

// ---- home / dashboard / search ----
export const getHome = () =>
  fetch(`${BASE}/api/home`, { cache: "no-store" }).then(json<Home>);

export const getDashboard = () =>
  fetch(`${BASE}/api/dashboard`, { cache: "no-store" }).then(json<Dashboard>);

export const search = (q: string) =>
  fetch(`${BASE}/api/search?q=${encodeURIComponent(q)}`, {
    cache: "no-store",
  }).then(json<{ results: SearchHit[]; mode: string }>);

export const getRecommend = (slug: string) =>
  fetch(`${BASE}/api/articles/${slug}/recommend`, { cache: "no-store" }).then(
    json<{ recommendations: Ref[] }>
  );

// ---- chat ----
export const chat = (question: string) =>
  fetch(`${BASE}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  }).then(json<{ answer: string; sources: Ref[] }>);

// ---- pcap ----
export const uploadPcap = (file: File) => {
  const form = new FormData();
  form.append("file", file);
  return fetch(`${BASE}/api/pcap`, { method: "POST", body: form }).then(
    json<PcapResult>
  );
};

// ---- progress / favorites / history ----
export const setProgress = (slug: string, completed: boolean) =>
  fetch(`${BASE}/api/progress`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ slug, completed }),
  }).then(json<{ ok: boolean }>);

export const addFavorite = (slug: string, title: string) =>
  fetch(`${BASE}/api/favorites`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ slug, title }),
  }).then(json<{ ok: boolean }>);

export const removeFavorite = (slug: string) =>
  fetch(`${BASE}/api/favorites/${slug}`, { method: "DELETE" }).then(
    json<{ ok: boolean }>
  );

export const getFavorites = () =>
  fetch(`${BASE}/api/favorites`, { cache: "no-store" }).then(
    json<{ favorites: (Ref & { created_at: string })[] }>
  );

export const getHistory = () =>
  fetch(`${BASE}/api/history`, { cache: "no-store" }).then(json<History>);
