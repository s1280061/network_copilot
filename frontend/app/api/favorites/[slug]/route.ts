import { NextRequest, NextResponse } from "next/server";

interface FavItem {
  slug: string;
  title: string;
  created_at: string;
}

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

export async function DELETE(
  req: NextRequest,
  { params }: { params: Promise<{ slug: string }> }
) {
  const { slug } = await params;
  const userId = req.nextUrl.searchParams.get("user_id") ?? "";
  if (!userId) return NextResponse.json({ error: "user_id required" }, { status: 400 });
  const favs = await getFavs(userId);
  await saveFavs(userId, favs.filter((f) => f.slug !== slug));
  return NextResponse.json({ ok: true });
}
