from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from ..db import add_comment, list_comments

router = APIRouter()


class CommentIn(BaseModel):
    user_id: str
    content: str

    @field_validator("user_id")
    @classmethod
    def validate_user_id(cls, v: str) -> str:
        v = v.strip()
        if not v or len(v) > 16:
            raise ValueError("user_id must be 1-16 chars")
        return v

    @field_validator("content")
    @classmethod
    def validate_content(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("content must not be empty")
        if len(v) > 1000:
            raise ValueError("content too long (max 1000 chars)")
        return v


@router.get("/api/comments/{slug}")
def get_comments(slug: str):
    return {"comments": list_comments(slug)}


@router.post("/api/comments/{slug}", status_code=201)
def post_comment(slug: str, body: CommentIn):
    comment = add_comment(slug, body.user_id, body.content)
    return comment
