"""Generate a static content bundle for the frontend so the 'ADAS note' is
fully readable on Vercel WITHOUT the backend running.

Run:  python -m app.gen_static
Output: ../frontend/lib/static-content.json

Re-run whenever articles change. When the backend is later deployed and the
frontend's NEXT_PUBLIC_API_BASE is set, the app uses the live API instead.
"""
import json
from pathlib import Path

from .services.content import (
    list_articles,
    get_article,
    roadmap_with_titles,
    CATEGORIES,
    _load_all,
)

OUT = Path(__file__).resolve().parent.parent.parent / "frontend" / "lib" / "static-content.json"


def _recommend(slug: str, titles: dict, k: int = 6) -> list[dict]:
    """Static recommendations: internal links + tag overlap (no RAG)."""
    articles = _load_all()
    base = articles[slug]["meta"]
    scores: dict[str, float] = {}
    for s in base.get("related", []) + base.get("next", []):
        if s != slug and s in titles:
            scores[s] = scores.get(s, 0.0) + 3.0
    base_tags = set(base.get("tags", []))
    for other, a in articles.items():
        if other == slug:
            continue
        overlap = base_tags & set(a["meta"].get("tags", []))
        if overlap:
            scores[other] = scores.get(other, 0.0) + 1.5 * len(overlap)
    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    return [{"slug": s, "title": titles[s]} for s, _ in ranked[:k]]


def main() -> None:
    titles = {a["slug"]: a["title"] for a in list_articles()}

    articles = []
    for a in list_articles():
        articles.append({**a, "views": 0, "completed": False, "favorite": False})

    by_slug = {}
    recommend = {}
    for slug in titles:
        art = get_article(slug)
        art["completed"] = False
        art["favorite"] = False
        by_slug[slug] = art
        recommend[slug] = _recommend(slug, titles)

    # roadmap (all not completed in static mode)
    levels = roadmap_with_titles()
    for lv in levels:
        for it in lv["items"]:
            it["completed"] = False
    total = sum(len(lv["items"]) for lv in levels)

    # home grouping
    by_cat = {c: [] for c in CATEGORIES}
    for a in articles:
        by_cat.setdefault(a["category"], []).append(a)
    categories = [{"name": c, "articles": by_cat.get(c, [])} for c in CATEGORIES]

    bundle = {
        "articles": articles,
        "bySlug": by_slug,
        "recommend": recommend,
        "roadmap": {"levels": levels, "progress": {"completed": 0, "total": total}},
        "home": {"categories": categories, "ranking": []},
    }

    OUT.write_text(json.dumps(bundle, ensure_ascii=False, indent=0), encoding="utf-8")
    print(f"wrote {OUT} ({len(articles)} articles)")


if __name__ == "__main__":
    main()
