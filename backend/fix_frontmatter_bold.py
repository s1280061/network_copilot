"""bold_keywords.py が frontmatter 内まで太字化してしまった `**` を除去する。

本文(body)はそのまま。先頭の --- ... --- の frontmatter 区間だけ `**` を消す。
"""
import re
from pathlib import Path

ARTICLES_DIR = Path(__file__).parent / "app" / "content" / "articles"
FM_RE = re.compile(r"^(---\s*\n)(.*?\n)(---\s*\n)(.*)$", re.DOTALL)

fixed = []
for path in sorted(ARTICLES_DIR.glob("*.md")):
    raw = path.read_text(encoding="utf-8")
    m = FM_RE.match(raw)
    if not m:
        continue
    fm = m.group(2)
    if "**" not in fm:
        continue
    new_fm = fm.replace("**", "")
    new_raw = m.group(1) + new_fm + m.group(3) + m.group(4)
    path.write_text(new_raw, encoding="utf-8")
    fixed.append(path.name)

print(f"Fixed {len(fixed)} files:")
for f in fixed:
    print(f"  {f}")
