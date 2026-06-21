"""engineering-notes のビルド済みPDFを network_copilot に同期する。

- engineering-notes の各 `NN_Name/main.pdf` を走査
- `frontend/public/notes/<slug>.pdf` にコピー
- `frontend/lib/notes.json` を更新（既存エントリの手書きメタ=title/description/icon/category は保持し、
  file/updated だけ最新化。新規ノートはデフォルト値で追加）

使い方:
    python sync_notes.py
    python sync_notes.py --notes-dir "D:/path/to/engineering-notes"

PDF自体のビルド（latexmk）はこのスクリプトの対象外。先にノート側でビルドしておくこと。
"""
import argparse
import datetime as dt
import json
import re
import shutil
from pathlib import Path

# 既定パス
DEFAULT_NOTES_DIR = Path(r"C:\Users\s1280\Desktop\engineering-notes")
REPO_ROOT = Path(__file__).resolve().parent.parent
PUBLIC_NOTES = REPO_ROOT / "frontend" / "public" / "notes"
NOTES_JSON = REPO_ROOT / "frontend" / "lib" / "notes.json"
GITHUB_BASE = "https://github.com/s1280061/engineering-notes/tree/main"

# ディレクトリ名 -> 表示用のヒント（無ければ汎用デフォルト）
ICON_BY_KEYWORD = {
    "network": "🌐", "os": "💻", "control": "🎛️", "signal": "📶",
    "math": "📐", "circuit": "⚡", "electronics": "⚡", "ml": "🤖",
    "security": "🔒", "automotive": "🚗", "wireless": "📡",
}
DEFAULT_ICON = "📘"

_NUM_PREFIX = re.compile(r"^\d+[_\-]?")


def slug_for(dir_name: str) -> str:
    """'01_Network' -> 'network'"""
    name = _NUM_PREFIX.sub("", dir_name)
    return name.strip().lower().replace(" ", "-").replace("_", "-")


def title_for(dir_name: str) -> str:
    name = _NUM_PREFIX.sub("", dir_name).replace("_", " ").strip()
    return f"{name}講義ノート"


def icon_for(slug: str) -> str:
    for kw, ic in ICON_BY_KEYWORD.items():
        if kw in slug:
            return ic
    return DEFAULT_ICON


def find_pdfs(notes_dir: Path) -> list[tuple[str, Path]]:
    """[(dir_name, pdf_path)] の一覧。各章ディレクトリ直下の main.pdf を採用。"""
    out = []
    for sub in sorted(notes_dir.iterdir()):
        if not sub.is_dir() or sub.name.startswith("."):
            continue
        pdf = sub / "main.pdf"
        if pdf.exists():
            out.append((sub.name, pdf))
    return out


def load_existing() -> dict[str, dict]:
    if NOTES_JSON.exists():
        data = json.loads(NOTES_JSON.read_text(encoding="utf-8"))
        return {e["slug"]: e for e in data}
    return {}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--notes-dir", default=str(DEFAULT_NOTES_DIR))
    args = ap.parse_args()
    notes_dir = Path(args.notes_dir)

    if not notes_dir.exists():
        raise SystemExit(f"engineering-notes が見つかりません: {notes_dir}")

    PUBLIC_NOTES.mkdir(parents=True, exist_ok=True)
    existing = load_existing()
    pdfs = find_pdfs(notes_dir)
    if not pdfs:
        raise SystemExit(f"main.pdf が1つも見つかりません: {notes_dir}")

    result: list[dict] = []
    for dir_name, pdf in pdfs:
        slug = slug_for(dir_name)
        dest = PUBLIC_NOTES / f"{slug}.pdf"
        shutil.copyfile(pdf, dest)
        updated = dt.date.fromtimestamp(pdf.stat().st_mtime).isoformat()
        size_kb = dest.stat().st_size // 1024

        if slug in existing:
            # 手書きメタは保持。file/updated だけ最新化。
            entry = dict(existing[slug])
            entry["file"] = f"/notes/{slug}.pdf"
            entry["updated"] = updated
            status = "update"
        else:
            entry = {
                "slug": slug,
                "title": title_for(dir_name),
                "category": _NUM_PREFIX.sub("", dir_name).replace("_", " ").strip(),
                "description": f"{title_for(dir_name)}（engineering-notes より自動同期）。説明は notes.json で編集できます。",
                "file": f"/notes/{slug}.pdf",
                "icon": icon_for(slug),
                "updated": updated,
                "source": f"{GITHUB_BASE}/{dir_name}",
            }
            status = "NEW"
        result.append(entry)
        print(f"  [{status}] {slug}  <- {dir_name}/main.pdf ({size_kb}KB)")

    # 既存にあったが今回 PDF が無くなったノートは残す（手動削除に委ねる）
    synced_slugs = {e["slug"] for e in result}
    for slug, entry in existing.items():
        if slug not in synced_slugs:
            result.append(entry)
            print(f"  [keep ] {slug} (今回PDFなし・notes.jsonには残す)")

    NOTES_JSON.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"\nSynced {len(pdfs)} PDF(s). notes.json: {len(result)} entries -> {NOTES_JSON}")


if __name__ == "__main__":
    main()
