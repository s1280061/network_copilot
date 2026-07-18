"""Learning content loader.

Reads Markdown articles (with YAML frontmatter) and the roadmap, converts
body to HTML, and resolves [[slug]] internal links into clickable anchors.
"""
import json
import re
from functools import lru_cache
from pathlib import Path

import markdown as md
import yaml

CONTENT_DIR = Path(__file__).resolve().parent.parent / "content"
ARTICLES_DIR = CONTENT_DIR / "articles"
ROADMAP_FILE = CONTENT_DIR / "roadmap.json"

_FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n(.*)$", re.DOTALL)
_LINK_RE = re.compile(r"\[\[([a-z0-9\-]+)\]\]")

# note-style top categories shown on the home screen.
CATEGORIES = ["Ethernet", "TCP/IP", "PCAP", "SOME/IP", "AUTOSAR", "SDV", "Automotive Bus", "Diagnostics", "Security", "Howto", "Python", "アルゴリズム", "C言語", "CAD/設計", "制御工学", "Statistics", "ML", "DL", "GenAI", "CV", "Electronics", "Automotive", "Wireless"]

# slug -> category (overridable via frontmatter `category`).
_CATEGORY_MAP = {
    "ethernet": "Ethernet",
    "mac-address": "Ethernet",
    "osi": "TCP/IP",
    "communication-basics": "TCP/IP",
    "ip": "TCP/IP",
    "tcp": "TCP/IP",
    "udp": "TCP/IP",
    "port": "TCP/IP",
    "socket": "PCAP",
    "wireshark": "PCAP",
    "pcap": "PCAP",
    "some-ip": "SOME/IP",
    "can": "AUTOSAR",
    "autosar": "AUTOSAR",
    "ros2-dds": "SDV",
    "sdv": "SDV",
    "adas-comm": "SDV",
    "lin": "Automotive Bus",
    "flexray": "Automotive Bus",
    "ptp": "Ethernet",
    "avtp": "Ethernet",
    "uds": "Diagnostics",
    "xcp": "Diagnostics",
    "doip": "Diagnostics",
    "adaptive-autosar": "AUTOSAR",
    "ota": "SDV",
    "v2x": "SDV",
    "cybersecurity": "Security",
    "howto-wireshark-someip": "Howto",
    "howto-tcpdump-capture": "Howto",
    "howto-ping-ecu": "Howto",
    "howto-doip-connect": "Howto",
    "howto-uds-dtc": "Howto",
    "howto-tshark-filter": "Howto",
    "howto-vlan-check": "Howto",
    "howto-pcap-analyze": "Howto",
    "micro-autobox": "SDV",
    "ipv4-ipv6": "TCP/IP",
    # Scapy
    "scapy-basics":      "PCAP",
    "scapy-pcap":        "PCAP",
    "scapy-automotive":  "PCAP",
    # Deep Learning
    "deep-learning":      "DL",
    "pytorch":            "DL",
    "cnn":                "DL",
    "rnn-lstm":           "DL",
    "gpu-architecture":   "DL",
    "nvidia-gpu-lineup":  "DL",
    # Generative AI
    "transformer":          "GenAI",
    "llm":                  "GenAI",
    "prompt-engineering":   "GenAI",
    "rag":                  "GenAI",
    # Computer Vision
    "opencv":              "CV",
    "image-processing":    "CV",
    # Machine Learning
    "ml-basics":          "ML",
    "scikit-learn":       "ML",
    "linear-regression":  "ML",
    "classification":     "ML",
    "gradient-boosting":  "ML",
    # Python Data Science
    "python-basics": "Python",
    "numpy": "Python",
    "pandas": "Python",
    "matplotlib": "Python",
    "seaborn": "Python",
    "data-cleaning": "Python",
    "data-analysis": "Python",
    "statistics": "Statistics",
    "fastapi": "Python",
    "time-series-analysis": "Python",
    "bayesian-statistics":   "Statistics",
    "hypothesis-testing":    "Statistics",
    "regression-analysis":   "Statistics",
    "time-series-statistics": "Statistics",
    "multivariate-statistics": "Statistics",
    # ML additional
    "evaluation-metrics": "ML",
    "clustering": "ML",
    "dimensionality-reduction": "ML",
    "anomaly-detection": "ML",
    # DL additional
    "generative-models": "DL",
    # CV additional
    "object-detection": "CV",
    "clip": "CV",
    "blip": "CV",
    "qformer": "CV",
    # GenAI additional
    "langchain": "GenAI",
    "fine-tuning": "GenAI",
    # アルゴリズム
    "fourier-analysis":        "Statistics",
    "p-value":                 "Statistics",
    "hierarchical-clustering": "ML",
    "big-o-notation":    "アルゴリズム",
    "data-structures":   "アルゴリズム",
    "sorting-algorithms": "アルゴリズム",
    "search-algorithms": "アルゴリズム",
    # C言語
    "c-basics":    "C言語",
    "c-pointers":  "C言語",
    "c-structs":   "C言語",
    # CAD/設計
    "cad-basics":              "CAD/設計",
    "3d-math":                 "CAD/設計",
    "orthographic-projection": "CAD/設計",
    "third-angle-projection":  "CAD/設計",
    "engineering-sketch":      "CAD/設計",
    # 制御工学
    "laplace-transform":    "制御工学",
    "transfer-function":    "制御工学",
    "block-diagram":        "制御工学",
    "control-engineering":  "制御工学",
    "matlab-simulink":      "制御工学",
    "auto-parking-control": "制御工学",
    # Automotive
    "engineering-drawing":       "Automotive",
    "automotive-torque":         "Automotive",
    "automotive-engine":         "Automotive",
    "automotive-transmission":   "Automotive",
    "automotive-electrical":     "Automotive",
    "ev-battery":                "Automotive",
    # Wireless
    "wireless-basics":           "Wireless",
    "wifi":                      "Wireless",
    "bluetooth":                 "Wireless",
    "lte-5g":                    "Wireless",
    "v2x-wireless":              "Wireless",
    "gnss":                      "Wireless",
    # Electronics
    "electricity-basics":        "Electronics",
    "ohms-law":                  "Electronics",
    "circuit-series-parallel":   "Electronics",
    "electric-power":            "Electronics",
    "electric-field":            "Electronics",
    "magnetism":                 "Electronics",
    "electromagnetic-induction": "Electronics",
    "capacitor":                 "Electronics",
    "alternating-current":       "Electronics",
    "semiconductor":             "Electronics",
}


def _difficulty_for(level: int) -> str:
    if level <= 2:
        return "初級"
    if level == 3:
        return "中級"
    return "上級"


def _parse_file(path: Path) -> dict:
    raw = path.read_text(encoding="utf-8")
    m = _FRONTMATTER_RE.match(raw)
    if not m:
        meta, body = {}, raw
    else:
        meta = yaml.safe_load(m.group(1)) or {}
        body = m.group(2)
    meta.setdefault("slug", path.stem)
    meta.setdefault("title", path.stem)
    meta.setdefault("level", 0)
    meta.setdefault("related", [])
    meta.setdefault("next", [])
    meta.setdefault("tags", [])
    meta.setdefault("category", _CATEGORY_MAP.get(meta["slug"], "TCP/IP"))
    meta.setdefault("difficulty", _difficulty_for(int(meta["level"])))
    # updated date: frontmatter `updated` or file mtime.
    if "updated" not in meta:
        import datetime as _dt

        meta["updated"] = _dt.date.fromtimestamp(path.stat().st_mtime).isoformat()
    else:
        meta["updated"] = str(meta["updated"])
    return {"meta": meta, "body": body}


def raw_body(slug: str) -> str:
    a = _load_all().get(slug)
    return a["body"] if a else ""


def article_meta(slug: str) -> dict | None:
    a = _load_all().get(slug)
    return a["meta"] if a else None


def split_sections(body: str) -> list[dict]:
    """Split markdown into {heading, text} chunks by '##' headings for RAG."""
    chunks: list[dict] = []
    heading = ""
    buf: list[str] = []

    def flush():
        text = "\n".join(buf).strip()
        if text:
            chunks.append({"heading": heading, "text": text})

    for line in body.splitlines():
        if line.startswith("## "):
            flush()
            heading = line[3:].strip()
            buf = []
        else:
            buf.append(_LINK_RE.sub(lambda m: m.group(1), line))
    flush()
    return chunks


@lru_cache
def _load_all() -> dict:
    """slug -> {meta, body}. Cached; titles needed for link resolution."""
    items = {}
    for f in sorted(ARTICLES_DIR.glob("*.md")):
        parsed = _parse_file(f)
        items[parsed["meta"]["slug"]] = parsed
    return items


def _titles() -> dict:
    return {slug: a["meta"]["title"] for slug, a in _load_all().items()}


def _prerequisites() -> dict:
    """slug -> list of prerequisite slugs.

    Derived as the reverse of `next` links (if A.next contains B, then A is a
    prerequisite of B), merged with any explicit `prereq` in frontmatter.
    """
    prereq: dict[str, list[str]] = {}
    for slug, a in _load_all().items():
        for nxt in a["meta"].get("next", []):
            prereq.setdefault(nxt, [])
            if slug not in prereq[nxt]:
                prereq[nxt].append(slug)
    # explicit overrides/additions
    for slug, a in _load_all().items():
        for p in a["meta"].get("prereq", []):
            prereq.setdefault(slug, [])
            if p not in prereq[slug]:
                prereq[slug].insert(0, p)
    return prereq


_CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
_MATH_PATTERNS = [
    re.compile(r"\$\$.*?\$\$", re.DOTALL),   # block  $$ ... $$
    re.compile(r"\\\[.*?\\\]", re.DOTALL),   # block  \[ ... \]
    re.compile(r"\\\(.*?\\\)", re.DOTALL),   # inline \( ... \)
]


def _protect_math(body: str) -> tuple[str, list[str]]:
    """Replace math spans with inert placeholders so the Markdown converter
    doesn't mangle LaTeX (strip backslashes, turn `_`/`*` into emphasis, etc.).
    Fenced code blocks are left untouched. Returns (protected_body, store)."""
    store: list[str] = []

    def protect_segment(seg: str) -> str:
        for pat in _MATH_PATTERNS:
            def repl(m: re.Match) -> str:
                store.append(m.group(0))
                return f"@@MATH{len(store) - 1}MATH@@"

            seg = pat.sub(repl, seg)
        return seg

    out: list[str] = []
    last = 0
    for m in _CODE_FENCE_RE.finditer(body):
        out.append(protect_segment(body[last:m.start()]))
        out.append(m.group(0))  # code block untouched
        last = m.end()
    out.append(protect_segment(body[last:]))
    return "".join(out), store


def _restore_math(html: str, store: list[str]) -> str:
    for i, s in enumerate(store):
        html = html.replace(f"@@MATH{i}MATH@@", s)
    return html


def _resolve_links(body: str) -> str:
    """Replace [[slug]] with a markdown link to /glossary/slug using the title."""
    titles = _titles()

    def repl(m: re.Match) -> str:
        slug = m.group(1)
        title = titles.get(slug, slug)
        # Custom marker class so the frontend can intercept for SPA navigation.
        return f'<a class="term-link" data-slug="{slug}" href="/glossary/{slug}">{title}</a>'

    return _LINK_RE.sub(repl, body)


def list_articles() -> list[dict]:
    """Metadata only, for the glossary grid."""
    out = []
    for a in _load_all().values():
        meta = a["meta"]
        # first paragraph of 概要 as a short excerpt
        excerpt = _first_paragraph(a["body"])
        out.append({**meta, "excerpt": excerpt})
    return sorted(out, key=lambda x: (x["level"], x["title"]))


def get_article(slug: str) -> dict | None:
    a = _load_all().get(slug)
    if not a:
        return None
    # resolve links first (on raw markdown), then convert to HTML.
    body = _resolve_links(a["body"])
    # shield LaTeX math from the Markdown converter, then restore it verbatim.
    body, math_store = _protect_math(body)
    html = md.markdown(body, extensions=["extra"])
    html = _restore_math(html, math_store)
    titles = _titles()
    meta = a["meta"]
    related = [{"slug": s, "title": titles.get(s, s)} for s in meta["related"] if s in titles]
    nxt = [{"slug": s, "title": titles.get(s, s)} for s in meta["next"] if s in titles]
    prereq_slugs = _prerequisites().get(slug, [])
    prereq = [{"slug": s, "title": titles.get(s, s)} for s in prereq_slugs if s in titles]
    return {
        **meta,
        "html": html,
        "prereq_full": prereq,
        "related_full": related,
        "next_full": nxt,
    }


def get_roadmap_raw() -> dict:
    return json.loads(ROADMAP_FILE.read_text(encoding="utf-8"))


def roadmap_with_titles() -> list[dict]:
    titles = _titles()
    data = get_roadmap_raw()
    levels = []
    for lv in data["levels"]:
        items = [{"slug": s, "title": titles.get(s, s)} for s in lv["items"]]
        levels.append({**lv, "items": items})
    return levels


def _first_paragraph(body: str) -> str:
    for line in body.splitlines():
        s = line.strip()
        if s and not s.startswith("#") and not s.startswith("---"):
            return _LINK_RE.sub(lambda m: m.group(1), s)[:120]
    return ""
