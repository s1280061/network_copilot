"""Static knowledge base: glossary, roadmap, and offline (mock) answers.

Kept separate so it can grow into CAN / SOME-IP / AUTOSAR content later
without touching the API layer.
"""

GLOSSARY = {
    "payload": {
        "term": "Payload",
        "definition": "プロトコルが運ぶ実データ本体。ヘッダ等の制御情報を除いた部分。",
        "image": "封筒(ヘッダ)の中身の手紙(ペイロード)。",
        "practice": "SOME/IPではサービスのメソッド引数がペイロードに載る。解析時はここを抽出して中身を確認する。",
    },
    "frame": {
        "term": "Frame",
        "definition": "データリンク層(L2)のデータ単位。EthernetフレームはMACアドレスを含む。",
        "image": "電車の1両。先頭(ヘッダ)と荷物(ペイロード)を持つ。",
        "practice": "車載Ethernetのトラブルでは、まずフレームのFCSエラーやVLANタグを確認する。",
    },
    "packet": {
        "term": "Packet",
        "definition": "ネットワーク層(L3)のデータ単位。IPヘッダ(送信元/宛先IP)を含む。",
        "image": "宛先住所が書かれた小包。",
        "practice": "ルーティング設計やMTU/フラグメント問題の調査で単位として扱う。",
    },
    "socket": {
        "term": "Socket",
        "definition": "IPアドレスとポート番号の組で表される通信エンドポイント。",
        "image": "電話番号(IP)+内線番号(ポート)。",
        "practice": "ECU上のアプリはUDP/TCPソケットを開いて通信する。SOME/IPもソケット上で動く。",
    },
    "mac address": {
        "term": "MAC Address",
        "definition": "ネットワーク機器に割り振られる48bitの物理アドレス。",
        "image": "機器固有の製造番号のような識別子。",
        "practice": "車載スイッチのMACテーブルや、ARPによるIP↔MAC解決の調査で使う。",
    },
    "vlan": {
        "term": "VLAN",
        "definition": "1本の物理Ethernetを論理的に分割する技術(IEEE 802.1Q)。",
        "image": "1本のケーブルに色分けされた仮想レーンを作る。",
        "practice": "車載Ethernetでは制御系/情報系トラフィックをVLANで分離する。",
    },
    "some/ip": {
        "term": "SOME/IP",
        "definition": "車載向けサービス指向通信ミドルウェア(Scalable service-Oriented MiddlewarE over IP)。",
        "image": "ECU同士の『サービスの注文・配達』の仕組み。",
        "practice": "AUTOSAR Adaptive環境でECU間のメソッド呼び出し/イベント通知に使われる。主にUDP/TCP上。",
    },
}

ROADMAP = [
    {
        "level": "1. 基礎",
        "topics": ["OSI参照モデル", "Ethernet / Frame", "MAC Address", "VLAN"],
    },
    {
        "level": "2. ネットワーク層",
        "topics": ["IPv4 / IPv6", "ARP", "ICMP", "ルーティングの基礎"],
    },
    {
        "level": "3. トランスポート層",
        "topics": ["TCP", "UDP", "Socket通信", "ポートの概念"],
    },
    {
        "level": "4. 車載アプリ層",
        "topics": ["SOME/IP", "DDS (ROS2)", "サービス指向アーキテクチャ"],
    },
    {
        "level": "5. 車載ネットワーク全般",
        "topics": ["CAN / CAN FD", "AUTOSAR (Classic/Adaptive)", "車載Ethernet設計"],
    },
]

# Rule-based offline answers used when AI_PROVIDER=mock or no key is set.
_OFFLINE = {
    "ethernet": {
        "beginner": "Ethernetは有線LANの基礎となるL1/L2技術で、MACアドレスを使って同じネットワーク内の機器同士がフレーム単位でデータをやり取りします。",
        "practice": "車載ではCAN/LINに代わる高帯域バックボーンとして車載Ethernet(100BASE-T1等)が採用され、カメラ映像やSOME/IP通信を運びます。",
        "related": ["Frame", "MAC Address", "VLAN", "スイッチング"],
        "next": ["IPv4", "ARP", "VLAN"],
    },
    "udp": {
        "beginner": "UDPはコネクションレスで再送制御を持たない軽量なトランスポートプロトコルです。速いが信頼性は保証しません。",
        "practice": "低遅延が重要なADAS ECU間通信やSOME/IPのイベント通知、映像ストリームで多用されます。",
        "related": ["TCP", "Socket", "SOME/IP"],
        "next": ["TCP", "SOME/IP"],
    },
    "tcp": {
        "beginner": "TCPはコネクション型で、3wayハンドシェイク・再送・順序保証・フロー制御を備えた信頼性の高いプロトコルです。",
        "practice": "確実性が必要な診断通信(DoIP)や大きなファイル転送に使われます。",
        "related": ["UDP", "Socket", "DoIP"],
        "next": ["UDP", "輻輳制御"],
    },
    "some/ip": {
        "beginner": "SOME/IPは車載ECU同士がサービス(メソッド呼び出しやイベント)をやり取りするためのIP上のミドルウェアです。",
        "practice": "AUTOSAR Adaptive環境で、カメラやセンサーECUが提供するサービスを他ECUが購読する形で使われます。",
        "related": ["UDP", "TCP", "Service Discovery", "AUTOSAR"],
        "next": ["AUTOSAR Adaptive", "DDS"],
    },
    "osi": {
        "beginner": "OSI参照モデルは通信機能を7階層(物理/データリンク/ネットワーク/トランスポート/セッション/プレゼンテーション/アプリケーション)に分けた概念モデルです。",
        "practice": "障害解析時に『どの層の問題か』を切り分ける共通言語として使います。EthernetはL2、IPはL3、TCP/UDPはL4。",
        "related": ["Ethernet", "IP", "TCP/UDP"],
        "next": ["TCP/IP 4階層モデル"],
    },
}


def lookup_glossary(query: str):
    q = (query or "").strip().lower()
    if not q:
        return list(GLOSSARY.values())
    hits = [v for k, v in GLOSSARY.items() if q in k or q in v["term"].lower()]
    return hits or list(GLOSSARY.values())


def offline_answer(question: str) -> str:
    q = (question or "").lower()
    key = None
    if "osi" in q:
        key = "osi"
    elif "some" in q:
        key = "some/ip"
    elif "udp" in q and "tcp" in q:
        key = "udp"
    elif "udp" in q:
        key = "udp"
    elif "tcp" in q:
        key = "tcp"
    elif "ethernet" in q or "イーサ" in q:
        key = "ethernet"

    if not key:
        return (
            "（オフラインモード）ご質問: "
            f"「{question}」\n\n"
            "現在AI APIキーが未設定のため、簡易回答のみ提供しています。"
            "Ethernet / TCP / UDP / SOME/IP / OSI などのキーワードを含めて質問するか、"
            "backend/.env に APIキーを設定してください。"
        )

    a = _OFFLINE[key]
    return (
        f"# 一言説明\n{a['beginner']}\n\n"
        f"# 詳細解説\n{a['beginner']}\n\n"
        f"# 自動運転での利用例\n{a['practice']}\n\n"
        f"# 関連知識\n- " + "\n- ".join(a["related"]) + "\n\n"
        f"# 次に学ぶべきこと\n- " + "\n- ".join(a["next"])
    )
