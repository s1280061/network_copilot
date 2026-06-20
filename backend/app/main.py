from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .db import init_db
from .knowledge import lookup_glossary
from .routers import chat, pcap, content, progress, home, search, comments

settings = get_settings()
app = FastAPI(title="Network Learning Copilot API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://localhost:3000"],
    # Allow Vercel production + preview deployments (*.vercel.app).
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _startup() -> None:
    init_db()
    # Auto-embed new/changed articles into ChromaDB (diff-based; no-op if RAG off).
    try:
        from .services.rag import reindex

        report = reindex()
        print(f"[rag] startup reindex: {report}")
    except Exception as exc:  # noqa: BLE001
        print(f"[rag] reindex skipped: {exc}")


@app.get("/api/health")
def health():
    return {"status": "ok", "ai_provider": settings.ai_provider}


# Legacy keyword glossary (kept for quick term search in the sidebar)
@app.get("/api/glossary-search")
def glossary_search(q: str = ""):
    return {"results": lookup_glossary(q)}


app.include_router(content.router)
app.include_router(chat.router)
app.include_router(pcap.router)
app.include_router(progress.router)
app.include_router(home.router)
app.include_router(search.router)
app.include_router(comments.router)
