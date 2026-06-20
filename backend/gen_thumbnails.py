"""サムネ画像がない記事を Pollinations AI で生成し public/thumbnails に保存する。

- static-content.json から slug / title / category を読む
- すでに画像がある記事はスキップ
- カテゴリ別にプロンプトのテイストを変える
- 並列ダウンロード + リトライ
"""
import json
import sys
import time
from pathlib import Path
from urllib.parse import quote

import urllib.request

# Pollinations 無料枠は 429 を返しやすいので、リクエスト間隔を空けて逐次実行する。
REQUEST_INTERVAL_SEC = 6

ROOT = Path(__file__).resolve().parent.parent
SC_FILE = ROOT / "frontend" / "lib" / "static-content.json"
THUMB_DIR = ROOT / "frontend" / "public" / "thumbnails"

# カテゴリ -> 画像スタイル（プロンプト末尾）
CATEGORY_STYLE = {
    "Ethernet": "automotive ethernet network technical illustration",
    "TCP/IP": "computer network protocol technical illustration",
    "PCAP": "network packet analysis technical illustration",
    "SOME/IP": "automotive software communication technical illustration",
    "AUTOSAR": "automotive ECU software architecture illustration",
    "SDV": "software defined vehicle futuristic illustration",
    "Automotive Bus": "automotive CAN bus wiring technical illustration",
    "Diagnostics": "automotive diagnostic tool technical illustration",
    "Security": "automotive cybersecurity shield technical illustration",
    "Howto": "engineer using network analysis tool, technical illustration",
    "Python": "python programming data science illustration",
    "アルゴリズム": "computer science algorithm abstract illustration",
    "C言語": "C programming low level code illustration",
    "CAD/設計": "CAD mechanical engineering drawing illustration",
    "Statistics": "data statistics charts graphs illustration",
    "ML": "machine learning AI abstract illustration",
    "DL": "deep learning neural network abstract illustration",
    "GenAI": "generative AI futuristic abstract illustration",
    "CV": "computer vision image recognition illustration",
    "Electronics": "electronics circuit board technical illustration",
    "Automotive": "automotive engineering mechanical illustration",
    "Wireless": "wireless communication antenna signal illustration",
}
DEFAULT_STYLE = "technical engineering illustration"
COMMON = "professional, clean, dark blue and white theme, flat vector style, no text, no words"


def build_prompt(title: str, category: str) -> str:
    style = CATEGORY_STYLE.get(category, DEFAULT_STYLE)
    return f"{title}, {style}, {COMMON}"


def pollinations_url(title: str, category: str, seed: int) -> str:
    prompt = quote(build_prompt(title, category))
    return (
        f"https://image.pollinations.ai/prompt/{prompt}"
        f"?width=640&height=360&nologo=true&seed={seed}&model=flux"
    )


def existing_slugs() -> set[str]:
    out = set()
    if THUMB_DIR.exists():
        for f in THUMB_DIR.iterdir():
            if f.is_file():
                out.add(f.stem.lower())
    return out


def download(slug: str, title: str, category: str, retries: int = 4) -> tuple[str, bool, str]:
    url = pollinations_url(title, category, seed=len(slug) + 7)
    dest = THUMB_DIR / f"{slug}.jpg"
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = resp.read()
            if len(data) < 1000:  # 失敗時の小さなエラー画像対策
                raise ValueError(f"too small ({len(data)} bytes)")
            dest.write_bytes(data)
            return slug, True, f"{len(data)//1024}KB"
        except Exception as exc:  # noqa: BLE001
            msg = str(exc)
            if attempt == retries:
                return slug, False, msg
            # 429 のときは長めにバックオフする
            backoff = 15 * attempt if "429" in msg else 4 * attempt
            time.sleep(backoff)
    return slug, False, "unknown"


def main() -> None:
    THUMB_DIR.mkdir(parents=True, exist_ok=True)
    sc = json.loads(SC_FILE.read_text(encoding="utf-8"))
    articles = sc["articles"]
    have = existing_slugs()

    todo = [
        (a["slug"], a["title"], a.get("category", ""))
        for a in articles
        if a["slug"].lower() not in have
    ]
    print(f"Articles: {len(articles)} / Have: {len(have)} / To generate: {len(todo)}")
    if not todo:
        print("Nothing to do.")
        return

    ok, fail = 0, []
    # 429 回避のため逐次 + 一定間隔。fail した分は再実行で続きから埋まる。
    for i, (slug, title, category) in enumerate(todo, 1):
        slug, success, info = download(slug, title, category)
        status = "OK " if success else "FAIL"
        print(f"  [{i}/{len(todo)}] {status} {slug} ({info})", flush=True)
        if success:
            ok += 1
        else:
            fail.append(slug)
        if i < len(todo):
            time.sleep(REQUEST_INTERVAL_SEC)

    print(f"\nDone. success={ok} fail={len(fail)}")
    if fail:
        print("Failed slugs (re-run to retry):", ", ".join(fail))
        sys.exit(1)


if __name__ == "__main__":
    main()
