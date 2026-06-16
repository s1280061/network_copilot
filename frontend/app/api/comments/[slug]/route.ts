import { NextRequest, NextResponse } from "next/server";

// ---------------------------------------------------------------------------
// In-memory store (survives across warm Lambda invocations on Vercel).
// Falls back to Upstash Redis if UPSTASH_REDIS_REST_URL + TOKEN are set.
// ---------------------------------------------------------------------------

interface Comment {
  id: number;
  slug: string;
  user_id: string;
  content: string;
  created_at: string;
}

// Global in-memory store (per-instance, persists across warm requests)
const memStore = new Map<string, Comment[]>();
let nextId = 1;

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
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ value: JSON.stringify(comments) }),
    });
  } catch {}
}

async function getComments(slug: string): Promise<Comment[]> {
  // Try Redis first
  const fromRedis = await redisGet(slug);
  if (fromRedis !== null) return fromRedis;
  // Fall back to memory
  return memStore.get(slug) ?? [];
}

async function saveComment(slug: string, user_id: string, content: string): Promise<Comment> {
  const comments = await getComments(slug);
  const comment: Comment = {
    id: nextId++,
    slug,
    user_id,
    content,
    created_at: new Date().toLocaleString("ja-JP", { timeZone: "Asia/Tokyo" }),
  };
  comments.push(comment);

  // Persist
  const fromRedis = await redisGet(slug);
  if (fromRedis !== null) {
    await redisSet(slug, comments);
  } else {
    memStore.set(slug, comments);
  }
  return comment;
}

// ---------------------------------------------------------------------------
// Route handlers
// ---------------------------------------------------------------------------

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ slug: string }> }
) {
  const { slug } = await params;
  const comments = await getComments(slug);
  return NextResponse.json({ comments });
}

export async function POST(
  req: NextRequest,
  { params }: { params: Promise<{ slug: string }> }
) {
  const { slug } = await params;
  const body = await req.json();
  const user_id = String(body.user_id ?? "").trim().slice(0, 16);
  const content = String(body.content ?? "").trim().slice(0, 1000);

  if (!user_id || !content) {
    return NextResponse.json({ error: "user_id and content required" }, { status: 400 });
  }

  const comment = await saveComment(slug, user_id, content);
  return NextResponse.json(comment, { status: 201 });
}
