"""各記事の重要キーワード・数値・定義を太字にするスクリプト"""
import re
from pathlib import Path

ARTICLES_DIR = Path(__file__).parent / "app" / "content" / "articles"

# slug -> [(検索パターン, 置換文字列), ...]
# 先頭から順に適用。すでに **...** で囲まれているものはスキップ。
BOLD_RULES: dict[str, list[tuple[str, str]]] = {
"communication-basics": [
    ("車載ネットワーク", "**車載ネットワーク**"),
    ("ゲートウェイECU", "**ゲートウェイECU**"),
    ("100BASE-T1", "**100BASE-T1**"),
    ("CAN（Controller Area Network）", "**CAN（Controller Area Network）**"),
],
"osi": [
    ("7層", "**7層**"),
    ("物理層", "**物理層**"),
    ("データリンク層", "**データリンク層**"),
    ("ネットワーク層", "**ネットワーク層**"),
    ("トランスポート層", "**トランスポート層**"),
    ("アプリケーション層", "**アプリケーション層**"),
    ("カプセル化", "**カプセル化**"),
],
"ethernet": [
    ("100BASE-T1", "**100BASE-T1**"),
    ("1000BASE-T1", "**1000BASE-T1**"),
    ("MACアドレス", "**MACアドレス**"),
    ("フレーム", "**フレーム**"),
    ("スイッチ", "**スイッチ**"),
    ("全二重通信", "**全二重通信**"),
],
"mac-address": [
    ("48ビット", "**48ビット**"),
    ("OUI", "**OUI**"),
    ("ユニキャスト", "**ユニキャスト**"),
    ("ブロードキャスト", "**ブロードキャスト**"),
    ("マルチキャスト", "**マルチキャスト**"),
    ("MACアドレステーブル", "**MACアドレステーブル**"),
],
"arp": [
    ("Address Resolution Protocol", "**Address Resolution Protocol**"),
    ("ブロードキャスト", "**ブロードキャスト**"),
    ("ARPテーブル", "**ARPテーブル**"),
    ("ARP Request", "**ARP Request**"),
    ("ARP Reply", "**ARP Reply**"),
    ("ARPスプーフィング", "**ARPスプーフィング**"),
],
"ip": [
    ("32ビット", "**32ビット**"),
    ("TTL", "**TTL**"),
    ("ルーティング", "**ルーティング**"),
    ("サブネット", "**サブネット**"),
    ("IPアドレス", "**IPアドレス**"),
    ("フラグメンテーション", "**フラグメンテーション**"),
],
"tcp": [
    ("3ウェイハンドシェイク", "**3ウェイハンドシェイク**"),
    ("SYN", "**SYN**"),
    ("ACK", "**ACK**"),
    ("再送制御", "**再送制御**"),
    ("フロー制御", "**フロー制御**"),
    ("輻輳制御", "**輻輳制御**"),
    ("コネクション指向", "**コネクション指向**"),
],
"udp": [
    ("コネクションレス", "**コネクションレス**"),
    ("低遅延", "**低遅延**"),
    ("順序保証なし", "**順序保証なし**"),
    ("リアルタイム", "**リアルタイム**"),
    ("マルチキャスト", "**マルチキャスト**"),
],
"port": [
    ("0〜65535", "**0〜65535**"),
    ("ウェルノウンポート", "**ウェルノウンポート**"),
    ("13400", "**13400**"),
    ("ポート番号", "**ポート番号**"),
    ("多重化", "**多重化**"),
],
"icmp": [
    ("Echo Request", "**Echo Request**"),
    ("Echo Reply", "**Echo Reply**"),
    ("TTL超過", "**TTL超過**"),
    ("到達不能", "**到達不能**"),
    ("ping", "**ping**"),
    ("traceroute", "**traceroute**"),
],
"subnet": [
    ("サブネットマスク", "**サブネットマスク**"),
    ("CIDR", "**CIDR**"),
    ("ネットワークアドレス", "**ネットワークアドレス**"),
    ("ブロードキャストアドレス", "**ブロードキャストアドレス**"),
    ("ホストアドレス", "**ホストアドレス**"),
    ("セグメント分割", "**セグメント分割**"),
],
"dhcp": [
    ("Discover", "**Discover**"),
    ("Offer", "**Offer**"),
    ("Request", "**Request**"),
    ("ACK", "**ACK**"),
    ("リース期間", "**リース期間**"),
    ("動的割り当て", "**動的割り当て**"),
],
"dns": [
    ("ドメイン名", "**ドメイン名**"),
    ("名前解決", "**名前解決**"),
    ("再帰クエリ", "**再帰クエリ**"),
    ("キャッシュ", "**キャッシュ**"),
    ("Aレコード", "**Aレコード**"),
    ("TTL", "**TTL**"),
],
"vlan": [
    ("IEEE 802.1Q", "**IEEE 802.1Q**"),
    ("VLANタグ", "**VLANタグ**"),
    ("トランクポート", "**トランクポート**"),
    ("アクセスポート", "**アクセスポート**"),
    ("VLAN ID", "**VLAN ID**"),
    ("ネットワーク分離", "**ネットワーク分離**"),
],
"socket": [
    ("ソケット", "**ソケット**"),
    ("ファイルディスクリプタ", "**ファイルディスクリプタ**"),
    ("bind", "**bind**"),
    ("listen", "**listen**"),
    ("accept", "**accept**"),
    ("connect", "**connect**"),
    ("ブロッキング", "**ブロッキング**"),
],
"wireshark": [
    ("パケットキャプチャ", "**パケットキャプチャ**"),
    ("表示フィルタ", "**表示フィルタ**"),
    ("キャプチャフィルタ", "**キャプチャフィルタ**"),
    ("dissector", "**dissector**"),
    ("フォロー TCPストリーム", "**フォロー TCPストリーム**"),
    ("プロミスキャスモード", "**プロミスキャスモード**"),
],
"pcap": [
    ("libpcap", "**libpcap**"),
    ("グローバルヘッダ", "**グローバルヘッダ**"),
    ("パケットヘッダ", "**パケットヘッダ**"),
    ("タイムスタンプ", "**タイムスタンプ**"),
    ("pcapng", "**pcapng**"),
],
"tcpdump": [
    ("-i", "**-i**"),
    ("-w", "**-w**"),
    ("-r", "**-r**"),
    ("-n", "**-n**"),
    ("BPFフィルタ", "**BPFフィルタ**"),
    ("インターフェース", "**インターフェース**"),
],
"tshark": [
    ("-Y", "**-Y**"),
    ("-T fields", "**-T fields**"),
    ("-z", "**-z**"),
    ("表示フィルタ", "**表示フィルタ**"),
    ("統計情報", "**統計情報**"),
    ("自動化", "**自動化**"),
],
"can": [
    ("11ビットID", "**11ビットID**"),
    ("29ビットID", "**29ビットID**"),
    ("CSMA/CA", "**CSMA/CA**"),
    ("アービトレーション", "**アービトレーション**"),
    ("最大8バイト", "**最大8バイト**"),
    ("1Mbps", "**1Mbps**"),
    ("差動信号", "**差動信号**"),
],
"can-fd": [
    ("最大64バイト", "**最大64バイト**"),
    ("最大8Mbps", "**最大8Mbps**"),
    ("ビットレートスイッチング", "**ビットレートスイッチング**"),
    ("BRS", "**BRS**"),
    ("後方互換性", "**後方互換性**"),
],
"some-ip": [
    ("Service ID", "**Service ID**"),
    ("Method ID", "**Method ID**"),
    ("SOME/IP-SD", "**SOME/IP-SD**"),
    ("サービスディスカバリ", "**サービスディスカバリ**"),
    ("Subscribe", "**Subscribe**"),
    ("Notification", "**Notification**"),
    ("シリアライゼーション", "**シリアライゼーション**"),
],
"autosar": [
    ("RTE（Runtime Environment）", "**RTE（Runtime Environment）**"),
    ("SWC（Software Component）", "**SWC（Software Component）**"),
    ("BSW（Basic Software）", "**BSW（Basic Software）**"),
    ("COM", "**COM**"),
    ("MCAL", "**MCAL**"),
    ("ポートインターフェース", "**ポートインターフェース**"),
],
"doip": [
    ("13400番ポート", "**13400番ポート**"),
    ("論理アドレス", "**論理アドレス**"),
    ("Routing Activation", "**Routing Activation**"),
    ("Vehicle Discovery", "**Vehicle Discovery**"),
    ("UDP", "**UDP**"),
    ("診断メッセージ転送", "**診断メッセージ転送**"),
],
"ros2-dds": [
    ("DDS（Data Distribution Service）", "**DDS（Data Distribution Service）**"),
    ("Publisher", "**Publisher**"),
    ("Subscriber", "**Subscriber**"),
    ("トピック", "**トピック**"),
    ("QoS", "**QoS**"),
    ("Discovery", "**Discovery**"),
],
"sdv": [
    ("ソフトウェア定義車両", "**ソフトウェア定義車両**"),
    ("OTA", "**OTA**"),
    ("HPC", "**HPC**"),
    ("ゾーンアーキテクチャ", "**ゾーンアーキテクチャ**"),
    ("API", "**API**"),
],
"adas-comm": [
    ("センサフュージョン", "**センサフュージョン**"),
    ("帯域幅", "**帯域幅**"),
    ("レイテンシ", "**レイテンシ**"),
    ("AVTP", "**AVTP**"),
    ("SOME/IP", "**SOME/IP**"),
    ("決定論的通信", "**決定論的通信**"),
],
"tsn": [
    ("IEEE 802.1AS", "**IEEE 802.1AS**"),
    ("IEEE 802.1Qbv", "**IEEE 802.1Qbv**"),
    ("時刻同期", "**時刻同期**"),
    ("帯域予約", "**帯域予約**"),
    ("スケジューリング", "**スケジューリング**"),
    ("最悪遅延保証", "**最悪遅延保証**"),
    ("CBS（Credit Based Shaper）", "**CBS（Credit Based Shaper）**"),
],
"uds": [
    ("サービスID", "**サービスID**"),
    ("0x10", "**0x10**"),
    ("0x22", "**0x22**"),
    ("0x19", "**0x19**"),
    ("0x14", "**0x14**"),
    ("ポジティブレスポンス", "**ポジティブレスポンス**"),
    ("ネガティブレスポンス", "**ネガティブレスポンス**"),
    ("DTC（Diagnostic Trouble Code）", "**DTC（Diagnostic Trouble Code）**"),
    ("診断セッション", "**診断セッション**"),
],
"lin": [
    ("マスター/スレーブ", "**マスター/スレーブ**"),
    ("最大20kbps", "**最大20kbps**"),
    ("スケジュールテーブル", "**スケジュールテーブル**"),
    ("Break フィールド", "**Break フィールド**"),
    ("シングルワイヤ", "**シングルワイヤ**"),
    ("低コスト", "**低コスト**"),
],
"flexray": [
    ("最大10Mbps", "**最大10Mbps**"),
    ("TDMA", "**TDMA**"),
    ("静的セグメント", "**静的セグメント**"),
    ("動的セグメント", "**動的セグメント**"),
    ("冗長性", "**冗長性**"),
    ("決定論的", "**決定論的**"),
    ("時刻同期", "**時刻同期**"),
],
"ptp": [
    ("IEEE 1588", "**IEEE 1588**"),
    ("グランドマスター", "**グランドマスター**"),
    ("Sync", "**Sync**"),
    ("Delay_Req", "**Delay_Req**"),
    ("オフセット補正", "**オフセット補正**"),
    ("サブマイクロ秒", "**サブマイクロ秒**"),
    ("gPTP", "**gPTP**"),
],
"adaptive-autosar": [
    ("ara::", "**ara::**"),
    ("ara::com", "**ara::com**"),
    ("動的サービスディスカバリ", "**動的サービスディスカバリ**"),
    ("POSIX", "**POSIX**"),
    ("実行管理", "**実行管理**"),
    ("高性能SoC", "**高性能SoC**"),
],
"ota": [
    ("差分更新", "**差分更新**"),
    ("署名検証", "**署名検証**"),
    ("ロールバック", "**ロールバック**"),
    ("A/Bパーティション", "**A/Bパーティション**"),
    ("TLS", "**TLS**"),
    ("整合性チェック", "**整合性チェック**"),
],
"v2x": [
    ("V2V（Vehicle to Vehicle）", "**V2V（Vehicle to Vehicle）**"),
    ("V2I（Vehicle to Infrastructure）", "**V2I（Vehicle to Infrastructure）**"),
    ("V2N（Vehicle to Network）", "**V2N（Vehicle to Network）**"),
    ("DSRC", "**DSRC**"),
    ("C-V2X", "**C-V2X**"),
    ("協調型自動運転", "**協調型自動運転**"),
],
"cybersecurity": [
    ("SecOC（Secure Onboard Communication）", "**SecOC（Secure Onboard Communication）**"),
    ("EVITA", "**EVITA**"),
    ("脅威分析", "**脅威分析**"),
    ("TARA", "**TARA**"),
    ("IDS（侵入検知システム）", "**IDS（侵入検知システム）**"),
    ("ファイアウォール", "**ファイアウォール**"),
    ("暗号化", "**暗号化**"),
    ("ISO/SAE 21434", "**ISO/SAE 21434**"),
],
"avtp": [
    ("IEEE 1722", "**IEEE 1722**"),
    ("gPTPタイムスタンプ", "**gPTPタイムスタンプ**"),
    ("CVF（Compressed Video Format）", "**CVF（Compressed Video Format）**"),
    ("AAF（AVTP Audio Format）", "**AAF（AVTP Audio Format）**"),
    ("EtherType 0x22F0", "**EtherType 0x22F0**"),
    ("同期再生", "**同期再生**"),
],
"xcp": [
    ("DAQ（Data Acquisition）", "**DAQ（Data Acquisition）**"),
    ("STIM（Stimulation）", "**STIM（Stimulation）**"),
    ("シードアンドキー", "**シードアンドキー**"),
    ("ODT（Object Descriptor Table）", "**ODT（Object Descriptor Table）**"),
    ("リアルタイム計測", "**リアルタイム計測**"),
    ("パラメータ書き換え", "**パラメータ書き換え**"),
],
"howto-ping-ecu": [
    ("ping", "**ping**"),
    ("疎通確認", "**疎通確認**"),
    ("TTL", "**TTL**"),
    ("ARP", "**ARP**"),
    ("ip addr show", "**ip addr show**"),
    ("ip route", "**ip route**"),
],
"howto-vlan-check": [
    ("vlan.id", "**vlan.id**"),
    ("IEEE 802.1Q", "**IEEE 802.1Q**"),
    ("トランクポート", "**トランクポート**"),
    ("タグ付きフレーム", "**タグ付きフレーム**"),
],
"howto-tcpdump-capture": [
    ("-i eth0", "**-i eth0**"),
    ("-w", "**-w**"),
    ("-s 0", "**-s 0**"),
    ("-C", "**-C**"),
    ("BPFフィルタ", "**BPFフィルタ**"),
    ("ローテーション", "**ローテーション**"),
],
"howto-tshark-filter": [
    ("-Y", "**-Y**"),
    ("-T fields", "**-T fields**"),
    ("-e", "**-e**"),
    ("-z", "**-z**"),
    ("パイプライン処理", "**パイプライン処理**"),
    ("一括解析", "**一括解析**"),
],
"howto-wireshark-someip": [
    ("someip", "**someip**"),
    ("サービスID", "**サービスID**"),
    ("メソッドID", "**メソッドID**"),
    ("IO Graph", "**IO Graph**"),
    ("プロトコル自動認識", "**プロトコル自動認識**"),
],
"howto-pcap-analyze": [
    ("-z io,phs", "**-z io,phs**"),
    ("プロトコル分布", "**プロトコル分布**"),
    ("異常パターン", "**異常パターン**"),
    ("再送パケット", "**再送パケット**"),
    ("tcp.analysis.retransmission", "**tcp.analysis.retransmission**"),
],
"howto-doip-connect": [
    ("13400", "**13400**"),
    ("Routing Activation", "**Routing Activation**"),
    ("Vehicle Announcement", "**Vehicle Announcement**"),
    ("論理アドレス", "**論理アドレス**"),
    ("TCP接続", "**TCP接続**"),
],
"howto-uds-dtc": [
    ("0x10 0x03", "**0x10 0x03**"),
    ("0x19 0x02", "**0x19 0x02**"),
    ("0x14", "**0x14**"),
    ("拡張診断セッション", "**拡張診断セッション**"),
    ("DTC読み出し", "**DTC読み出し**"),
    ("DTCクリア", "**DTCクリア**"),
],
}


def _already_bold(text: str, phrase: str) -> bool:
    """フレーズがすでに **...** で囲まれているか確認"""
    return f"**{phrase}**" in text


def bold_article(slug: str, rules: list[tuple[str, str]]) -> None:
    path = ARTICLES_DIR / f"{slug}.md"
    if not path.exists():
        print(f"  SKIP (not found): {slug}.md")
        return
    content = path.read_text(encoding="utf-8")

    # コードブロックと図解セクション以外の範囲だけ処理
    # 簡易的に: コードブロック行は変換しない
    lines = content.split("\n")
    in_code = False
    result = []
    changed = False

    for line in lines:
        if line.strip().startswith("```"):
            in_code = not in_code
        if in_code or line.startswith("#"):
            result.append(line)
            continue

        new_line = line
        for phrase, replacement in rules:
            if phrase in new_line and not _already_bold(new_line, phrase):
                new_line = new_line.replace(phrase, replacement, 1)
                changed = True
        result.append(new_line)

    if changed:
        path.write_text("\n".join(result), encoding="utf-8")
        print(f"  OK: {slug}.md")
    else:
        print(f"  NO CHANGE: {slug}.md")


if __name__ == "__main__":
    print(f"Bolding keywords in {len(BOLD_RULES)} articles...")
    for slug, rules in BOLD_RULES.items():
        bold_article(slug, rules)
    print("Done.")
