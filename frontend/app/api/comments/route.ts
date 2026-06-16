import { NextResponse } from "next/server";
import { getAllComments } from "./store";

export async function GET() {
  const all = await getAllComments();
  return NextResponse.json({ comments: all });
}
