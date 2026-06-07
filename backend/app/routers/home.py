from fastapi import APIRouter

from ..services.content import list_articles, CATEGORIES
from ..db import view_counts, ranking, completed_slugs, list_favorites

router = APIRouter(prefix="/api", tags=["home"])


def _enrich(items: list[dict]) -> list[dict]:
    views = view_counts()
    done = completed_slugs()
    favs = {f["slug"] for f in list_favorites()}
    for a in items:
        a["views"] = views.get(a["slug"], 0)
        a["completed"] = a["slug"] in done
        a["favorite"] = a["slug"] in favs
    return items


@router.get("/home")
def home():
    items = _enrich(list_articles())
    by_category = {c: [] for c in CATEGORIES}
    for a in items:
        by_category.setdefault(a["category"], []).append(a)
    categories = [
        {"name": c, "articles": by_category.get(c, [])} for c in CATEGORIES
    ]
    return {"categories": categories, "ranking": ranking(limit=10)}


@router.get("/ranking")
def get_ranking(period: str = "all"):
    days = 7 if period == "week" else None
    return {"ranking": ranking(limit=10, days=days)}


@router.get("/dashboard")
def dashboard():
    items = list_articles()
    done = completed_slugs()
    by_cat: dict[str, dict] = {}
    for a in items:
        c = a["category"]
        by_cat.setdefault(c, {"category": c, "total": 0, "completed": 0})
        by_cat[c]["total"] += 1
        if a["slug"] in done:
            by_cat[c]["completed"] += 1
    categories = list(by_cat.values())
    for c in categories:
        c["rate"] = round(c["completed"] / c["total"] * 100) if c["total"] else 0
    total = len(items)
    completed = sum(1 for a in items if a["slug"] in done)
    return {
        "total": total,
        "completed": completed,
        "rate": round(completed / total * 100) if total else 0,
        "categories": categories,
    }
