from fastapi import APIRouter, HTTPException

from ..services.content import (
    list_articles,
    get_article,
    roadmap_with_titles,
)
from ..db import completed_slugs, record_view, list_favorites

router = APIRouter(prefix="/api", tags=["content"])


@router.get("/roadmap")
def roadmap():
    done = completed_slugs()
    levels = roadmap_with_titles()
    for lv in levels:
        for item in lv["items"]:
            item["completed"] = item["slug"] in done
    total = sum(len(lv["items"]) for lv in levels)
    completed = sum(1 for lv in levels for it in lv["items"] if it["completed"])
    return {
        "levels": levels,
        "progress": {"completed": completed, "total": total},
    }


@router.get("/articles")
def articles():
    done = completed_slugs()
    favs = {f["slug"] for f in list_favorites()}
    items = list_articles()
    for a in items:
        a["completed"] = a["slug"] in done
        a["favorite"] = a["slug"] in favs
    return {"articles": items}


@router.get("/articles/{slug}")
def article(slug: str):
    a = get_article(slug)
    if not a:
        raise HTTPException(status_code=404, detail="article not found")
    done = completed_slugs()
    favs = {f["slug"] for f in list_favorites()}
    a["completed"] = slug in done
    a["favorite"] = slug in favs
    record_view(slug, a["title"])
    return a
