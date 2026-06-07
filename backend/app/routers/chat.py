from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..services.ai import ask_ai
from ..services import rag
from ..db import save_chat

router = APIRouter(prefix="/api", tags=["chat"])


class ChatRequest(BaseModel):
    question: str


@router.post("/chat")
async def chat(req: ChatRequest):
    if not req.question.strip():
        raise HTTPException(status_code=400, detail="question is required")

    # RAG: retrieve relevant articles, use as context + cite as sources.
    sources = rag.search(req.question, k=3)
    context = ""
    if sources:
        context = (
            "以下は関連する学習記事の見出しです。回答の参考にしてください:\n"
            + "\n".join(f"- {s['title']} ({s.get('heading','')})" for s in sources)
        )

    answer = await ask_ai(req.question, context)
    save_chat(req.question, answer)
    return {
        "answer": answer,
        "sources": [{"slug": s["slug"], "title": s["title"]} for s in sources],
    }
