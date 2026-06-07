"""RAG layer: semantic search over articles using ChromaDB + a local
multilingual embedding model (fastembed / multilingual-e5-small, ONNX, no torch).

Designed to degrade gracefully: if chromadb/fastembed are not installed, the
module reports RAG_AVAILABLE = False and callers fall back to keyword/tag logic.

Article add workflow: reindex() diff-checks content hashes and re-embeds only
new/changed articles, so dropping a new .md and restarting is enough.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .content import _load_all, split_sections

_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
_CHROMA_DIR = _DATA_DIR / "chroma"
_HASH_FILE = _DATA_DIR / "rag_index.json"
_EMBED_MODEL = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
_COLLECTION = "articles"

RAG_AVAILABLE = False
_client = None
_collection = None
_embedder = None
_init_error = ""


def _lazy_init() -> bool:
    """Initialise chromadb + embedder once. Returns True if usable."""
    global RAG_AVAILABLE, _client, _collection, _embedder, _init_error
    if RAG_AVAILABLE:
        return True
    if _init_error:  # already failed once
        return False
    try:
        import chromadb
        from fastembed import TextEmbedding

        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        _client = chromadb.PersistentClient(path=str(_CHROMA_DIR))
        _collection = _client.get_or_create_collection(
            name=_COLLECTION, metadata={"hnsw:space": "cosine"}
        )
        _embedder = TextEmbedding(model_name=_EMBED_MODEL)
        RAG_AVAILABLE = True
        return True
    except Exception as exc:  # noqa: BLE001 - optional dependency
        _init_error = str(exc)
        return False


def _embed(texts: list[str], kind: str = "passage") -> list[list[float]]:
    """Embed texts. `kind` kept for API symmetry (this model needs no prefix)."""
    return [v.tolist() for v in _embedder.embed(list(texts))]


def _hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _load_hashes() -> dict:
    if _HASH_FILE.exists():
        return json.loads(_HASH_FILE.read_text(encoding="utf-8"))
    return {}


def _save_hashes(h: dict) -> None:
    _HASH_FILE.write_text(json.dumps(h, ensure_ascii=False), encoding="utf-8")


def reindex(force: bool = False) -> dict:
    """Embed new/changed articles into ChromaDB. Returns a small report."""
    if not _lazy_init():
        return {"available": False, "error": _init_error}

    articles = _load_all()
    old = {} if force else _load_hashes()
    new_hashes = {}
    changed = []

    for slug, a in articles.items():
        body = a["body"]
        meta = a["meta"]
        h = _hash(meta["title"] + body)
        new_hashes[slug] = h
        if old.get(slug) == h:
            continue
        changed.append(slug)

        # remove any previous chunks for this slug, then add fresh ones.
        _collection.delete(where={"slug": slug})
        sections = split_sections(body) or [{"heading": "", "text": body}]
        ids, docs, metadatas = [], [], []
        for i, sec in enumerate(sections):
            ids.append(f"{slug}::{i}")
            docs.append(sec["text"])
            metadatas.append(
                {
                    "slug": slug,
                    "title": meta["title"],
                    "category": meta["category"],
                    "heading": sec["heading"],
                }
            )
        embeddings = _embed(docs, "passage")
        _collection.add(ids=ids, documents=docs, embeddings=embeddings, metadatas=metadatas)

    # drop articles that no longer exist
    for slug in list(old):
        if slug not in articles:
            _collection.delete(where={"slug": slug})

    _save_hashes(new_hashes)
    return {"available": True, "indexed": len(articles), "changed": changed}


def search(query: str, k: int = 5) -> list[dict]:
    """Return distinct articles ranked by semantic similarity."""
    if not _lazy_init() or not query.strip():
        return []
    try:
        if _collection.count() == 0:
            reindex()
        q_emb = _embed([query], "query")
        res = _collection.query(query_embeddings=q_emb, n_results=k * 3)
    except Exception:  # noqa: BLE001
        return []

    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]
    seen: dict[str, dict] = {}
    for meta, dist in zip(metas, dists):
        slug = meta["slug"]
        score = 1.0 - float(dist)  # cosine distance -> similarity
        if slug not in seen or score > seen[slug]["score"]:
            seen[slug] = {
                "slug": slug,
                "title": meta["title"],
                "category": meta.get("category"),
                "heading": meta.get("heading"),
                "score": round(score, 3),
            }
    ranked = sorted(seen.values(), key=lambda x: x["score"], reverse=True)
    return ranked[:k]
