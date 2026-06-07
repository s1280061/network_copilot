"""Map detected protocols (from PCAP) to recommended learning articles,
and recommend related articles for a given article (tags + links + RAG)."""
from .content import _titles, _load_all, raw_body
from . import rag

# protocol name (as produced by analyzers/pcap.py) -> article slugs
_PROTO_TO_ARTICLES = {
    "Ethernet": ["ethernet", "mac-address"],
    "VLAN": ["ethernet"],
    "IPv4": ["ip"],
    "IPv6": ["ip"],
    "ARP": ["mac-address", "ip"],
    "ICMP": ["ip"],
    "TCP": ["tcp", "socket", "port"],
    "UDP": ["udp", "socket", "port"],
    "SOME/IP": ["some-ip", "udp"],
    "SOME/IP-SD": ["some-ip", "udp"],
    "DoIP": ["tcp", "ip"],
}


def recommend_from_protocols(protocols: dict) -> list[dict]:
    """Return de-duplicated article recommendations for detected protocols."""
    titles = _titles()
    seen: list[str] = []
    for proto in protocols:
        for slug in _PROTO_TO_ARTICLES.get(proto, []):
            if slug not in seen and slug in titles:
                seen.append(slug)
    return [{"slug": s, "title": titles[s]} for s in seen]


def recommend_note(protocols: dict) -> str:
    """Short human-readable note about the dominant transport protocol."""
    if protocols.get("UDP"):
        return "この通信ではUDPが使用されています。低遅延が求められるADAS通信で多用されます。"
    if protocols.get("TCP"):
        return "この通信ではTCPが使用されています。確実性が求められる診断やデータ転送で使われます。"
    return "検出されたプロトコルに対応する学習記事を推薦します。"


def recommend_for_article(slug: str, k: int = 6) -> list[dict]:
    """'あなたへのおすすめ': merge internal links, tag overlap, and RAG."""
    articles = _load_all()
    titles = _titles()
    base = articles.get(slug)
    if not base:
        return []
    meta = base["meta"]

    scores: dict[str, float] = {}

    # 1. internal links (strong signal)
    for s in meta.get("related", []) + meta.get("next", []):
        if s != slug and s in titles:
            scores[s] = scores.get(s, 0.0) + 3.0

    # 2. tag overlap
    base_tags = set(meta.get("tags", []))
    for other_slug, a in articles.items():
        if other_slug == slug:
            continue
        overlap = base_tags & set(a["meta"].get("tags", []))
        if overlap:
            scores[other_slug] = scores.get(other_slug, 0.0) + 1.5 * len(overlap)

    # 3. RAG semantic similarity (if available)
    if rag.RAG_AVAILABLE or rag._lazy_init():
        for hit in rag.search(meta["title"] + " " + raw_body(slug)[:500], k=k + 2):
            if hit["slug"] != slug:
                scores[hit["slug"]] = scores.get(hit["slug"], 0.0) + 2.0 * hit["score"]

    ranked = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    return [
        {"slug": s, "title": titles[s]}
        for s, _ in ranked
        if s in titles
    ][:k]
