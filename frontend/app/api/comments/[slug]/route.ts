import { NextRequest, NextResponse } from "next/server";
import { getCommentsForSlug, saveComment } from "../store";

export async function GET(
  _req: NextRequest,
  { params }: { params: Promise<{ slug: string }> }
) {
  const { slug } = await params;
  const comments = await getCommentsForSlug(slug);
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
