import sqlite3
from pathlib import Path
from contextlib import contextmanager

DB_PATH = Path(__file__).resolve().parent.parent / "data" / "copilot.db"


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_conn() as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS pcap_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                summary TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS favorites (
                slug TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS progress (
                slug TEXT PRIMARY KEY,
                completed_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS article_views (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT NOT NULL,
                title TEXT NOT NULL,
                viewed_at TEXT NOT NULL DEFAULT (datetime('now'))
            );

            CREATE TABLE IF NOT EXISTS comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                slug TEXT NOT NULL,
                user_id TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
            );
            """
        )
        conn.commit()


@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


# ---- chat / pcap ----
def save_chat(question: str, answer: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO chat_history (question, answer) VALUES (?, ?)",
            (question, answer),
        )
        conn.commit()


def save_pcap(filename: str, summary: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO pcap_history (filename, summary) VALUES (?, ?)",
            (filename, summary),
        )
        conn.commit()


def recent_chats(limit: int = 20):
    return _fetch(
        "SELECT id, question, answer, created_at FROM chat_history "
        "ORDER BY id DESC LIMIT ?",
        (limit,),
    )


def recent_pcaps(limit: int = 20):
    return _fetch(
        "SELECT id, filename, summary, created_at FROM pcap_history "
        "ORDER BY id DESC LIMIT ?",
        (limit,),
    )


# ---- favorites ----
def add_favorite(slug: str, title: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO favorites (slug, title) VALUES (?, ?)",
            (slug, title),
        )
        conn.commit()


def remove_favorite(slug: str) -> None:
    with get_conn() as conn:
        conn.execute("DELETE FROM favorites WHERE slug = ?", (slug,))
        conn.commit()


def list_favorites():
    return _fetch(
        "SELECT slug, title, created_at FROM favorites ORDER BY created_at DESC"
    )


# ---- progress ----
def set_progress(slug: str, completed: bool) -> None:
    with get_conn() as conn:
        if completed:
            conn.execute(
                "INSERT OR REPLACE INTO progress (slug) VALUES (?)", (slug,)
            )
        else:
            conn.execute("DELETE FROM progress WHERE slug = ?", (slug,))
        conn.commit()


def completed_slugs() -> set[str]:
    rows = _fetch("SELECT slug FROM progress")
    return {r["slug"] for r in rows}


# ---- article views (history) ----
def record_view(slug: str, title: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO article_views (slug, title) VALUES (?, ?)", (slug, title)
        )
        conn.commit()


def recent_views(limit: int = 30):
    return _fetch(
        "SELECT id, slug, title, viewed_at FROM article_views "
        "ORDER BY id DESC LIMIT ?",
        (limit,),
    )


def view_counts() -> dict:
    """slug -> total view count."""
    rows = _fetch("SELECT slug, COUNT(*) AS c FROM article_views GROUP BY slug")
    return {r["slug"]: r["c"] for r in rows}


def ranking(limit: int = 10, days: int | None = None):
    """Most-viewed articles, optionally within the last N days."""
    where = ""
    params: tuple = ()
    if days is not None:
        where = "WHERE viewed_at >= datetime('now', ?)"
        params = (f"-{days} days",)
    sql = (
        "SELECT slug, title, COUNT(*) AS views FROM article_views "
        f"{where} GROUP BY slug, title ORDER BY views DESC LIMIT ?"
    )
    return _fetch(sql, params + (limit,))


# ---- comments ----
def add_comment(slug: str, user_id: str, content: str) -> dict:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO comments (slug, user_id, content) VALUES (?, ?, ?)",
            (slug, user_id, content),
        )
        conn.commit()
        row = conn.execute(
            "SELECT id, slug, user_id, content, created_at FROM comments WHERE id = ?",
            (cur.lastrowid,),
        ).fetchone()
    return dict(row)


def list_comments(slug: str, limit: int = 200):
    return _fetch(
        "SELECT id, slug, user_id, content, created_at FROM comments "
        "WHERE slug = ? ORDER BY id ASC LIMIT ?",
        (slug, limit),
    )


def _fetch(sql: str, params: tuple = ()):
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [dict(r) for r in rows]
