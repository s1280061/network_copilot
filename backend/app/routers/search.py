from fastapi import APIRouter

from ..services import rag
from ..services.content import list_articles
from ..services.recommend import recommend_for_article

router = APIRouter(prefix="/api", tags=["search"])


@router.get("/search")
def search(q: str = "", k: int = 5):
    """Semantic search via RAG; falls back to keyword match if RAG is off."""
    if not q.strip():
        return {"results": [], "mode": "empty"}

    hits = rag.search(q, k=k)
    if hits:
        return {"results": hits, "mode": "semantic"}

    # fallback: keyword match over title/excerpt/tags
    ql = q.lower()
    results = []
    for a in list_articles():
        if (
            ql in a["title"].lower()
            or ql in (a.get("excerpt") or "").lower()
            or any(ql in t for t in a["tags"])
        ):
            results.append({"slug": a["slug"], "title": a["title"], "category": a["category"]})
    return {"results": results[:k], "mode": "keyword"}


@router.get("/articles/{slug}/recommend")
def recommend(slug: str):
    return {"recommendations": recommend_for_article(slug)}
