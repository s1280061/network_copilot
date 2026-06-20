import { NextRequest, NextResponse } from "next/server";

interface FavItem {
  slug: string;
  title: string;
  created_at: string;
}

// Global in-memory store keyed by user_id
const memStore = new Map<string, FavItem[]>();

async function redisGet(userId: string): Promise<FavItem[] | null> {
  const url = process.env.UPSTASH_REDIS_REST_URL;
  const token = process.env.UPSTASH_REDIS_REST_TOKEN;
  if (!url || !token) return null;
  try {
    const res = await fetch(`${url}/get/favorites:${userId}`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
    const d = await res.json();
    return d.result ? JSON.parse(d.result) : [];
  } catch {
    return null;
  }
}

async function redisSet(userId: string, favs: FavItem[]): Promise<void> {
  const url = process.env.UPSTASH_REDIS_REST_URL;
  const token = process.env.UPSTASH_REDIS_REST_TOKEN;
  if (!url || !token) return;
  try {
    await fetch(`${url}/set/favorites:${userId}`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ value: JSON.stringify(favs) }),
    });
  } catch {}
}

async function getFavs(userId: string): Promise<FavItem[]> {
  const fromRedis = await redisGet(userId);
  if (fromRedis !== null) return fromRedis;
  return memStore.get(userId) ?? [];
}

async function saveFavs(userId: string, favs: FavItem[]): Promise<void> {
  const fromRedis = await redisGet(userId);
  if (fromRedis !== null) {
    await redisSet(userId, favs);
  } else {
    memStore.set(userId, favs);
  }
}

export async function GET(req: NextRequest) {
  const userId = req.nextUrl.searchParams.get("user_id") ?? "";
  if (!userId) return NextResponse.json({ favorites: [] });
  const favorites = await getFavs(userId);
  return NextResponse.json({ favorites });
}

export async function POST(req: NextRequest) {
  const body = await req.json();
  const userId = String(body.user_id ?? "").trim().slice(0, 32);
  const slug = String(body.slug ?? "").trim().slice(0, 200);
  const title = String(body.title ?? "").trim().slice(0, 200);
  if (!userId || !slug) {
    return NextResponse.json({ error: "user_id and slug required" }, { status: 400 });
  }
  const favs = await getFavs(userId);
  if (!favs.some((f) => f.slug === slug)) {
    favs.unshift({ slug, title, created_at: new Date().toISOString() });
    await saveFavs(userId, favs);
  }
  return NextResponse.json({ ok: true });
}
