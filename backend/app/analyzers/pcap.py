"""PCAP analysis with Scapy.

Extracts Ethernet / VLAN / IPv4 / IPv6 / TCP / UDP / ARP / ICMP info and
builds a protocol-stack tree. Designed to be extended later with
CAN / SOME-IP analyzers (add a new module under analyzers/ and register it).
"""
from collections import Counter

from scapy.all import rdpcap
from scapy.layers.l2 import Ether, ARP, Dot1Q
from scapy.layers.inet import IP, TCP, UDP, ICMP
from scapy.layers.inet6 import IPv6


def analyze_pcap(path: str) -> dict:
    packets = rdpcap(path)

    proto_counter: Counter = Counter()
    peers: Counter = Counter()
    ports: Counter = Counter()
    stack_paths: Counter = Counter()

    for pkt in packets:
        layers = []

        if pkt.haslayer(Ether):
            proto_counter["Ethernet"] += 1
            layers.append("Ethernet")
        if pkt.haslayer(Dot1Q):
            proto_counter["VLAN"] += 1
            layers.append("VLAN")

        if pkt.haslayer(ARP):
            proto_counter["ARP"] += 1
            layers.append("ARP")
        if pkt.haslayer(IP):
            proto_counter["IPv4"] += 1
            layers.append("IPv4")
            peers[pkt[IP].src] += 1
            peers[pkt[IP].dst] += 1
        if pkt.haslayer(IPv6):
            proto_counter["IPv6"] += 1
            layers.append("IPv6")
            peers[pkt[IPv6].src] += 1
            peers[pkt[IPv6].dst] += 1
        if pkt.haslayer(ICMP):
            proto_counter["ICMP"] += 1
            layers.append("ICMP")

        if pkt.haslayer(TCP):
            proto_counter["TCP"] += 1
            layers.append("TCP")
            ports[pkt[TCP].sport] += 1
            ports[pkt[TCP].dport] += 1
            layers.append(_appguess(pkt[TCP].dport, pkt[TCP].sport))
        if pkt.haslayer(UDP):
            proto_counter["UDP"] += 1
            layers.append("UDP")
            ports[pkt[UDP].sport] += 1
            ports[pkt[UDP].dport] += 1
            layers.append(_appguess(pkt[UDP].dport, pkt[UDP].sport))

        layers = [l for l in layers if l]
        if layers:
            stack_paths[" > ".join(layers)] += 1

    return {
        "packet_count": len(packets),
        "protocols": dict(proto_counter.most_common()),
        "peers": [{"address": a, "count": c} for a, c in peers.most_common(20)],
        "ports": [{"port": p, "count": c} for p, c in ports.most_common(20)],
        "stacks": [{"path": s, "count": c} for s, c in stack_paths.most_common(10)],
        "mermaid": _build_mermaid(stack_paths),
    }


# Well-known / car-network port hints
_PORT_HINTS = {
    30490: "SOME/IP-SD",
    30491: "SOME/IP",
    13400: "DoIP",
    53: "DNS",
    67: "DHCP",
    68: "DHCP",
    123: "NTP",
    443: "HTTPS",
    80: "HTTP",
    22: "SSH",
}


def _appguess(dport: int, sport: int) -> str:
    for p in (dport, sport):
        if p in _PORT_HINTS:
            return _PORT_HINTS[p]
    if 30490 <= dport <= 30599 or 30490 <= sport <= 30599:
        return "SOME/IP"
    return ""


def _build_mermaid(stack_paths: Counter) -> str:
    """Build a Mermaid graph from observed protocol stacks."""
    edges = set()
    for path in stack_paths:
        nodes = path.split(" > ")
        for a, b in zip(nodes, nodes[1:]):
            edges.add((a, b))

    if not edges:
        return "graph TD\n  none[解析可能なレイヤがありません]"

    def nid(name: str) -> str:
        return name.replace("/", "_").replace("-", "_").replace(" ", "_")

    lines = ["graph TD"]
    for a, b in sorted(edges):
        lines.append(f"  {nid(a)}[{a}] --> {nid(b)}[{b}]")
    return "\n".join(lines)
