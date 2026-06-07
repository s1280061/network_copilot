from fastapi import APIRouter
from pydantic import BaseModel

from ..db import (
    add_favorite,
    remove_favorite,
    list_favorites,
    set_progress,
    completed_slugs,
    recent_views,
    recent_chats,
    recent_pcaps,
)

router = APIRouter(prefix="/api", tags=["progress"])


class FavoriteRequest(BaseModel):
    slug: str
    title: str


class ProgressRequest(BaseModel):
    slug: str
    completed: bool


@router.get("/favorites")
def get_favorites():
    return {"favorites": list_favorites()}


@router.post("/favorites")
def post_favorite(req: FavoriteRequest):
    add_favorite(req.slug, req.title)
    return {"ok": True}


@router.delete("/favorites/{slug}")
def delete_favorite(slug: str):
    remove_favorite(slug)
    return {"ok": True}


@router.post("/progress")
def post_progress(req: ProgressRequest):
    set_progress(req.slug, req.completed)
    return {"ok": True, "completed": sorted(completed_slugs())}


@router.get("/history")
def history():
    return {
        "views": recent_views(),
        "chats": recent_chats(),
        "pcaps": recent_pcaps(),
    }
