// Shared comment store.
// Uses Upstash Redis (via REST API) when env vars are set; otherwise in-memory.
// Set UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN in Vercel env vars
// to enable persistent storage across serverless invocations.

export interface Comment {
  id: number;
  slug: string;
  user_id: string;
  content: string;
  created_at: string;
}

// In-memory fallback (lost on cold start / new instance)
const memStore = new Map<string, Comment[]>();
let memNextId = 1;

// ---- Upstash Redis REST helpers ----
// Uses the pipeline/execute format: POST {url} body=["COMMAND","arg1","arg2"]

function redisEnv(): { url: string; token: string } | null {
  const url = process.env.UPSTASH_REDIS_REST_URL;
  const token = process.env.UPSTASH_REDIS_REST_TOKEN;
  if (!url || !token) return null;
  return { url, token };
}

async function redisCmd(env: { url: string; token: string }, ...args: string[]): Promise<unknown> {
  const res = await fetch(env.url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify(args),
    cache: "no-store",
  });
  const d = await res.json();
  return d.result;
}

async function redisGet(env: { url: string; token: string }, key: string): Promise<string | null> {
  const result = await redisCmd(env, "GET", key);
  return typeof result === "string" ? result : null;
}

async function redisSet(env: { url: string; token: string }, key: string, value: string): Promise<void> {
  await redisCmd(env, "SET", key, value);
}

async function redisScan(env: { url: string; token: string }, pattern: string): Promise<string[]> {
  // SCAN 0 MATCH pattern COUNT 1000
  const result = await redisCmd(env, "SCAN", "0", "MATCH", pattern, "COUNT", "1000") as [string, string[]];
  return Array.isArray(result) ? (result[1] ?? []) : [];
}

async function redisIncr(env: { url: string; token: string }, key: string): Promise<number> {
  const result = await redisCmd(env, "INCR", key);
  return typeof result === "number" ? result : 1;
}

// ---- Public API ----

export async function getCommentsForSlug(slug: string): Promise<Comment[]> {
  const env = redisEnv();
  if (env) {
    try {
      const raw = await redisGet(env, `comments:${slug}`);
      return raw ? JSON.parse(raw) : [];
    } catch { /* fall through to memory */ }
  }
  return memStore.get(slug) ?? [];
}

export async function getAllComments(): Promise<Comment[]> {
  const env = redisEnv();
  if (env) {
    try {
      const keys = await redisScan(env, "comments:*");
      const all: Comment[] = [];
      await Promise.all(
        keys
          .filter((k) => k.startsWith("comments:") && k !== "comments:_nextid")
          .map(async (key) => {
            const raw = await redisGet(env, key);
            if (raw) {
              try { all.push(...JSON.parse(raw)); } catch {}
            }
          })
      );
      return all;
    } catch { /* fall through */ }
  }
  const all: Comment[] = [];
  for (const comments of memStore.values()) all.push(...comments);
  return all;
}

export async function saveComment(slug: string, user_id: string, content: string): Promise<Comment> {
  const env = redisEnv();

  let id: number;
  if (env) {
    try {
      id = await redisIncr(env, "comments:_nextid");
    } catch {
      id = memNextId++;
    }
  } else {
    id = memNextId++;
  }

  const comment: Comment = {
    id,
    slug,
    user_id,
    content,
    created_at: new Date().toLocaleString("ja-JP", { timeZone: "Asia/Tokyo" }),
  };

  if (env) {
    try {
      const existing = await getCommentsForSlug(slug);
      existing.push(comment);
      await redisSet(env, `comments:${slug}`, JSON.stringify(existing));
      return comment;
    } catch { /* fall through to memory */ }
  }

  const existing = memStore.get(slug) ?? [];
  existing.push(comment);
  memStore.set(slug, existing);
  return comment;
}
