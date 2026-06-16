// Shared in-memory comment store + optional Upstash Redis persistence.
// Exported so both /api/comments and /api/comments/[slug] use the same instance.

export interface Comment {
  id: number;
  slug: string;
  user_id: string;
  content: string;
  created_at: string;
}

export const memStore = new Map<string, Comment[]>();
export let nextId = 1;
export function bumpId() { return nextId++; }

// ---- Redis helpers ----
async function redisGet(slug: string): Promise<Comment[] | null> {
  const url = process.env.UPSTASH_REDIS_REST_URL;
  const token = process.env.UPSTASH_REDIS_REST_TOKEN;
  if (!url || !token) return null;
  try {
    const res = await fetch(`${url}/get/comments:${slug}`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
    const d = await res.json();
    return d.result ? JSON.parse(d.result) : [];
  } catch {
    return null;
  }
}

async function redisSet(slug: string, comments: Comment[]): Promise<void> {
  const url = process.env.UPSTASH_REDIS_REST_URL;
  const token = process.env.UPSTASH_REDIS_REST_TOKEN;
  if (!url || !token) return;
  try {
    await fetch(`${url}/set/comments:${slug}`, {
      method: "POST",
      headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ value: JSON.stringify(comments) }),
    });
  } catch {}
}

// Redis scan: returns all keys matching comments:*
async function redisGetAll(): Promise<Comment[] | null> {
  const url = process.env.UPSTASH_REDIS_REST_URL;
  const token = process.env.UPSTASH_REDIS_REST_TOKEN;
  if (!url || !token) return null;
  try {
    const scanRes = await fetch(`${url}/scan/0/match/comments:*`, {
      headers: { Authorization: `Bearer ${token}` },
      cache: "no-store",
    });
    const scanData = await scanRes.json();
    const keys: string[] = scanData.result?.[1] ?? [];
    if (keys.length === 0) return [];
    const all: Comment[] = [];
    await Promise.all(
      keys.map(async (key) => {
        const slug = key.replace(/^comments:/, "");
        const comments = await redisGet(slug);
        if (comments) all.push(...comments);
      })
    );
    return all;
  } catch {
    return null;
  }
}

// ---- Public API ----
export async function getCommentsForSlug(slug: string): Promise<Comment[]> {
  const fromRedis = await redisGet(slug);
  if (fromRedis !== null) return fromRedis;
  return memStore.get(slug) ?? [];
}

export async function getAllComments(): Promise<Comment[]> {
  const fromRedis = await redisGetAll();
  if (fromRedis !== null) return fromRedis;
  // In-memory: collect all
  const all: Comment[] = [];
  for (const comments of memStore.values()) all.push(...comments);
  return all;
}

export async function saveComment(slug: string, user_id: string, content: string): Promise<Comment> {
  const comments = await getCommentsForSlug(slug);
  const comment: Comment = {
    id: bumpId(),
    slug,
    user_id,
    content,
    created_at: new Date().toLocaleString("ja-JP", { timeZone: "Asia/Tokyo" }),
  };
  comments.push(comment);

  const fromRedis = await redisGet(slug);
  if (fromRedis !== null) {
    await redisSet(slug, comments);
  } else {
    memStore.set(slug, comments);
  }
  return comment;
}
