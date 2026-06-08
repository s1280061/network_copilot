"""全記事にMermaid図解セクションを追加するスクリプト"""
from pathlib import Path

ARTICLES_DIR = Path(__file__).parent / "app" / "content" / "articles"

DIAGRAMS = {
"communication-basics": """
```mermaid
graph LR
  A[センサECU] -->|データ送信| G[ゲートウェイECU]
  G -->|転送| B[制御ECU]
  G -->|転送| C[IVIシステム]
  B -->|制御指令| D[アクチュエータ]
```
""",

"osi": """
```mermaid
graph TD
  L7["7. アプリケーション層　(SOME/IP, DoIP)"]
  L6["6. プレゼンテーション層　(暗号化・変換)"]
  L5["5. セッション層　(接続管理)"]
  L4["4. トランスポート層　(TCP / UDP)"]
  L3["3. ネットワーク層　(IP)"]
  L2["2. データリンク層　(Ethernet フレーム)"]
  L1["1. 物理層　(100BASE-T1 ケーブル)"]
  L7 --> L6 --> L5 --> L4 --> L3 --> L2 --> L1
```
""",

"ethernet": """
```mermaid
graph LR
  subgraph EthernetFrame["Ethernet フレーム"]
    DA["宛先MAC (6B)"] --- SA["送信元MAC (6B)"] --- ET["EtherType (2B)"] --- PL["ペイロード (46-1500B)"] --- FCS["FCS (4B)"]
  end
  CAM[カメラECU] -->|フレーム送信| SW[Ethernetスイッチ]
  SW -->|転送| ADC[ADASコントローラ]
```
""",

"mac-address": """
```mermaid
graph LR
  subgraph MAC["MACアドレス (48bit = 6オクテット)"]
    OUI["OUI (24bit)\nメーカー識別"] --- NIC["NIC固有番号 (24bit)"]
  end
  ECU1["TCU\n02:00:1A:BC:DE:F0"] -->|Ethernetフレーム| SW[スイッチ]
  SW --> ECU2["ゲートウェイECU\n02:00:1A:BC:DE:F1"]
```
""",

"arp": """
```mermaid
sequenceDiagram
  participant A as 診断PC (192.168.1.100)
  participant N as ネットワーク(ブロードキャスト)
  participant B as IVI ECU (192.168.1.3)
  A->>N: ARP Request: 192.168.1.3のMACは?
  N->>B: (全ノードへ転送)
  B->>A: ARP Reply: 02:00:1A:BC:DE:03
  Note over A: ARPテーブルに記録
```
""",

"ip": """
```mermaid
graph LR
  CAM["カメラECU\n192.168.1.10"] -->|IPパケット| GW["ゲートウェイECU\nルーティング"]
  GW --> IVI["IVIシステム\n10.0.0.20"]
  subgraph Packet["IPパケットヘッダ"]
    SRC["送信元: 192.168.1.10"] --- DST["宛先: 10.0.0.20"] --- TTL["TTL: 64"]
  end
```
""",

"tcp": """
```mermaid
sequenceDiagram
  participant C as 診断PC
  participant S as ゲートウェイECU
  C->>S: SYN
  S->>C: SYN-ACK
  C->>S: ACK (接続確立)
  C->>S: DATA (UDSリクエスト)
  S->>C: ACK + DATA (UDS応答)
  C->>S: FIN
  S->>C: FIN-ACK
```
""",

"udp": """
```mermaid
graph LR
  LIDAR["LiDARセンサECU"] -->|UDPデータグラム\n点群データ| ADC["ADASドメインコントローラ"]
  subgraph UDP["UDPの特徴"]
    F1["コネクションレス"] --- F2["低遅延"] --- F3["順序保証なし"]
  end
```
""",

"port": """
```mermaid
graph LR
  TCU["TCU (10.0.0.1)"] -->|":8080 OTAサービス"| DIAG[診断PC]
  TCU -->|":13400 DoIP診断"| DIAG
  TCU -->|":5555 ログ収集"| LOGGER[データロガーECU]
```
""",

"icmp": """
```mermaid
sequenceDiagram
  participant PC as 診断ワークステーション
  participant ECU as 車載ECU (LiDAR)
  PC->>ECU: ICMP Echo Request (ping)
  ECU->>PC: ICMP Echo Reply
  Note over PC: RTT = 0.8ms → 正常
  PC->>ECU: ICMP Echo Request
  Note over PC,ECU: タイムアウト → ECU不在 or IP設定ミス
```
""",

"subnet": """
```mermaid
graph TD
  GW["ゲートウェイECU"]
  subgraph A["Network A: 192.168.1.0/24 (ADAS)"]
    CAM["カメラECU .10"]
    LID["LiDARセンサ .11"]
  end
  subgraph B["Network B: 10.0.0.0/8 (IVI)"]
    IVI["IVIシステム .20"]
    TCU["TCU .50"]
  end
  GW --- CAM
  GW --- LID
  GW --- IVI
  GW --- TCU
```
""",

"dhcp": """
```mermaid
sequenceDiagram
  participant C as IVIシステム (新規起動)
  participant S as DHCPサーバー (ゲートウェイ)
  C->>S: DHCP Discover (ブロードキャスト)
  S->>C: DHCP Offer (IP: 192.168.1.50 提案)
  C->>S: DHCP Request (192.168.1.50 要求)
  S->>C: DHCP ACK (IP・サブネット・GW 確定)
```
""",

"dns": """
```mermaid
sequenceDiagram
  participant IVI as IVIシステム (クライアント)
  participant GW as DNSサーバー (ゲートウェイ)
  participant Cloud as 外部DNSサーバー
  IVI->>GW: クエリ: backend.service の IP は?
  GW->>Cloud: 再帰クエリ (キャッシュなし時)
  Cloud->>GW: 10.0.0.5
  GW->>IVI: 応答: 10.0.0.5
```
""",

"vlan": """
```mermaid
graph LR
  SW["Ethernetスイッチ"]
  subgraph VLAN10["VLAN 10 (ADASドメイン)"]
    CAM[カメラECU]
    ADC[ADASコントローラ]
  end
  subgraph VLAN20["VLAN 20 (IVI・診断)"]
    IVI[IVIシステム]
    TCU[テレマティクスECU]
  end
  CAM --- SW
  ADC --- SW
  IVI --- SW
  TCU --- SW
```
""",

"socket": """
```mermaid
sequenceDiagram
  participant App as DoIPアプリ (クライアント)
  participant OS as OS ソケット層
  participant ECU as ゲートウェイECU
  App->>OS: socket() + connect(192.168.1.1:13400)
  OS->>ECU: TCP SYN
  ECU->>OS: SYN-ACK
  OS->>App: 接続完了
  App->>OS: send(UDSリクエスト)
  OS->>ECU: TCP DATA
  ECU->>OS: TCP DATA (UDS応答)
  OS->>App: recv() → 応答データ
```
""",

"wireshark": """
```mermaid
graph LR
  ECU["車載ゲートウェイECU"] -->|Ethernet| PC["Wireshark\n(診断ワークステーション)"]
  PC --> PL["パケット一覧\nDoIP / SOME/IP / CAN"]
  PL --> PD["パケット詳細\nプロトコル解析"]
  PD --> PB["バイト列\n16進数生データ"]
```
""",

"pcap": """
```mermaid
graph LR
  ETH["車載Ethernet"] -->|パケットキャプチャ| LOGGER["診断ロガーECU"]
  LOGGER -->|pcapファイル保存| FILE["vehicle_traffic.pcap"]
  subgraph Structure["pcapファイル構造"]
    GH["グローバルヘッダ"] --- PH["パケットヘッダ×N"] --- DATA["パケットデータ×N"]
  end
  FILE --> WS["Wireshark / tshark\nで開いて解析"]
```
""",

"tcpdump": """
```mermaid
graph LR
  NW["車両ネットワーク\nTCP/UDP/DoIP"] --> ECU["組み込みECU\n(Linux OS)"]
  ECU -->|"tcpdump -i eth0 -w cap.pcap"| FILE["capture.pcap"]
  FILE -->|SCP転送| PC["診断PC\nWireshark解析"]
```
""",

"tshark": """
```mermaid
graph LR
  PCAP["vehicle_capture.pcap"] -->|"tshark -r -Y someip"| FILTER["フィルタ済みパケット"]
  FILTER -->|"-T fields -e someip.serviceid"| CSV["service_id 一覧"]
  PCAP -->|"-q -z io,phs"| STATS["プロトコル統計"]
```
""",

"can": """
```mermaid
graph LR
  ECU1["エンジンECU"] -->|CANフレーム| BUS["CAN バス\n(ツイストペア)"]
  ECU2["ブレーキECU"] -->|CANフレーム| BUS
  BUS --> ECU3["インスツルメント\nクラスタECU"]
  BUS --> ECU4["トランスミッション\nECU"]
  subgraph Frame["CAN フレーム"]
    ID["ID (11bit)"] --- DLC["DLC"] --- DATA["データ (最大8B)"] --- CRC["CRC"]
  end
```
""",

"can-fd": """
```mermaid
graph LR
  subgraph Classic["Classic CAN (最大8B)"]
    C1["ブレーキECU"] -->|"8B @ 1Mbps"| GW["ゲートウェイ\nECU"]
  end
  subgraph FD["CAN FD (最大64B)"]
    GW -->|"64B @ 5Mbps\nデータフェーズ"| CAM["カメラECU"]
    GW --> RAD["レーダーECU"]
  end
```
""",

"some-ip": """
```mermaid
sequenceDiagram
  participant C as クライアントECU (インフォテインメント)
  participant S as サーバーECU (ゲートウェイ)
  Note over C,S: SOME/IP-SD サービスディスカバリ
  S->>C: OfferService (Service ID: 0x1234)
  C->>S: SubscribeEventgroup
  S->>C: SubscribeEventgroupAck
  Note over C,S: 通常通信
  C->>S: Request (Method 0x0001)
  S->>C: Response
  S->>C: Notification (イベント通知)
```
""",

"autosar": """
```mermaid
graph TD
  APP["アプリケーション層\n(Brake Control / Lights Control)"]
  RTE["RTE: Runtime Environment\n(上位・下位の橋渡し)"]
  BSW["Basic Software (BSW)\nServices / Communication / Memory / I/O"]
  MCU["マイクロコントローラ"]
  APP --> RTE --> BSW --> MCU
```
""",

"doip": """
```mermaid
sequenceDiagram
  participant PC as 診断ワークステーション
  participant GW as ゲートウェイECU (DoIPエンティティ)
  participant ECU as ターゲットECU
  PC->>GW: Vehicle Discovery (UDP 13400)
  GW->>PC: Vehicle Announcement (IP + 論理アドレス)
  PC->>GW: Routing Activation Request (TCP 13400)
  GW->>PC: Routing Activation Response (成功)
  PC->>GW: UDS Request (診断コマンド)
  GW->>ECU: UDS転送 (CAN/Ethernet)
  ECU->>GW: UDS Response
  GW->>PC: UDS Response転送
```
""",

"ros2-dds": """
```mermaid
graph LR
  subgraph ADAS["ADASコンピュータ"]
    CAM_NODE["カメラノード\n(Publisher)"] -->|"/image_raw"| DDS["DDS データバス"]
    DDS --> PERC["認識ノード\n(Subscriber)"]
    PERC -->|"/objects"| DDS
    DDS --> PLAN["計画ノード\n(Subscriber)"]
  end
  LID["LiDARセンサ"] --> CAM_NODE
```
""",

"sdv": """
```mermaid
graph TD
  CLOUD["クラウドサービス\n(OTA / 診断 / データ収集)"]
  HPC["車両コンピューティングプラットフォーム\n(HPC / Adaptive AUTOSAR / ROS2)"]
  HW["車両ハードウェア\n(ECU / センサ / アクチュエータ)"]
  CLOUD <-->|"4G/5G"| HPC
  HPC <-->|"Ethernet / CAN"| HW
```
""",

"adas-comm": """
```mermaid
graph LR
  LID["LiDARセンサ"] -->|"UDP/AVTP\n点群データ"| ADC["ADASドメイン\nコントローラ"]
  CAM1["前方カメラECU"] -->|"AVTP\n映像ストリーム"| ADC
  CAM2["後方カメラECU"] -->|"AVTP"| ADC
  RAD["レーダーセンサ"] -->|"SOME/IP\n物体リスト"| ADC
  ADC -->|"センサフュージョン\n結果"| CTRL["車両制御ECU"]
```
""",

"tsn": """
```mermaid
sequenceDiagram
  participant SW as TSN対応スイッチ
  participant CTRL as ブレーキ制御ECU
  participant IVI as IVIシステム
  Note over SW: gPTP時刻同期 (PTP)
  SW->>CTRL: 制御データ (タイムスロット予約済み・遅延保証)
  SW->>IVI: 映像データ (ベストエフォート)
  Note over CTRL: 最悪遅延 < 500μs 保証
```
""",

"uds": """
```mermaid
sequenceDiagram
  participant PC as 診断ツール
  participant ECU as ターゲットECU
  PC->>ECU: 10 03 (ExtendedDiagnosticSession)
  ECU->>PC: 50 03 (PositiveResponse)
  PC->>ECU: 19 02 08 (ReadDTC, confirmedDTC)
  ECU->>PC: 59 02 08 [DTC1][DTC2]... (故障コード一覧)
  PC->>ECU: 22 F1 90 (ReadDID: VIN番号)
  ECU->>PC: 62 F1 90 [17バイトVIN]
```
""",

"lin": """
```mermaid
sequenceDiagram
  participant M as マスターECU
  participant S1 as スレーブ1 (ミラーモーター)
  participant S2 as スレーブ2 (シート調整)
  M->>S1: ヘッダ (Break + Sync + ID=0x10)
  S1->>M: レスポンス (モーター角度データ)
  M->>S2: ヘッダ (ID=0x20)
  S2->>M: レスポンス (シート位置データ)
  Note over M: スケジュール管理はマスターのみ
```
""",

"flexray": """
```mermaid
graph LR
  subgraph Cycle["FlexRay 通信サイクル"]
    ST["静的セグメント\n(TDMA固定スロット)\n安全クリティカルデータ"] --- DY["動的セグメント\n(FTDMA)\n優先度付きデータ"]
  end
  EPS["電子式パワー\nステアリング"] -->|"スロット固定\n遅延上限保証"| ST
  ESC["ESC"] -->|"スロット固定"| ST
  BCM["ボディ制御ECU"] -->|"空きスロット使用"| DY
```
""",

"ptp": """
```mermaid
sequenceDiagram
  participant M as グランドマスター (ADASコントローラ)
  participant S as スレーブECU (カメラ)
  M->>S: Sync (t1タイムスタンプ付き)
  Note over S: t2 = 受信時刻を記録
  S->>M: Delay_Req (t3タイムスタンプ)
  M->>S: Delay_Resp (t3を返送)
  Note over S: t4 = 受信時刻<br/>オフセット = ((t2-t1)-(t4-t3))/2<br/>サブマイクロ秒精度で補正
```
""",

"adaptive-autosar": """
```mermaid
graph TD
  AA["Adaptive Application\n(物体認識 / 経路計画 / 車線維持)"]
  ARA["ara:: API\n(com / exec / diag / update / crypto)"]
  OS["POSIX OS (Linux / QNX)"]
  HW["高性能SoC (GPU / NPU搭載)"]
  AA --> ARA --> OS --> HW
```
""",

"ota": """
```mermaid
sequenceDiagram
  participant Cloud as OTAクラウドサーバー
  participant TCU as テレマティクスECU
  participant OTA as OTAマネージャー
  participant ECU as ターゲットECU
  Cloud->>TCU: 差分パッケージ配信 (TLS暗号化)
  TCU->>TCU: 署名検証 (RSA/ECDSA)
  TCU->>OTA: パッケージ転送
  OTA->>ECU: UDS Download (0x34/0x36/0x37)
  ECU->>OTA: 整合性チェック完了
  ECU->>ECU: リセット・新FW起動
```
""",

"v2x": """
```mermaid
graph TD
  V["自車両"]
  V2V["V2V\n(車々間通信)\n他車の位置・速度"]
  V2I["V2I\n(路車間通信)\n信号・道路情報"]
  V2P["V2P\n(歩行者通信)\n歩行者スマホ"]
  V2N["V2N\n(ネットワーク)\n地図・OTA・遠隔監視"]
  V --- V2V
  V --- V2I
  V --- V2P
  V --- V2N
```
""",

"cybersecurity": """
```mermaid
graph TD
  EXT["外部インターフェース\n(V2X / OTA / Bluetooth / USB)"]
  FW["ファイアウォール\n(ゲートウェイECU)"]
  VLAN["VLANセグメント\nADAS / IVI / 診断を分離"]
  IDS["IDS (侵入検知)\n異常トラフィック監視"]
  SECOCC["SecOC\n(通信メッセージ認証)"]
  EXT -->|フィルタリング| FW --> VLAN --> IDS --> SECOCC
```
""",

"avtp": """
```mermaid
graph LR
  CAM["カメラECU×6"] -->|"AVTP (EtherType 0x22F0)\ngPTPタイムスタンプ付き"| SW["TSN対応\nEthernetスイッチ"]
  SW -->|"帯域予約 (CBS)"| ADC["ADASドメイン\nコントローラ"]
  ADC -->|センサフュージョン| CTRL["車両制御"]
  subgraph Format["AVTPサブタイプ"]
    CVF["CVF: H.264映像"] --- AAF["AAF: PCM音声"] --- CRF["CRF: 時刻参照"]
  end
```
""",

"xcp": """
```mermaid
sequenceDiagram
  participant Tool as キャリブレーションツール (INCA/CANape)
  participant ECU as ADASドメインコントローラ
  Tool->>ECU: CONNECT
  ECU->>Tool: PositiveResponse (セッション確立)
  Tool->>ECU: SET_DAQ_LIST (測定変数リスト登録)
  Tool->>ECU: START_STOP_DAQ (計測開始)
  ECU->>Tool: DAQパケット (センサ値 1kHz で送信)
  Tool->>ECU: DOWNLOAD (パラメータ書き換え)
  Note over Tool,ECU: リアルタイムに閾値を調整しながらログ取得
```
""",

"howto-wireshark-someip": """
```mermaid
graph LR
  PCAP["vehicle.pcap\nまたはLiveキャプチャ"] --> WS["Wireshark"]
  WS -->|"フィルタ: someip"| LIST["SOME/IPパケット一覧"]
  LIST --> DET["パケット詳細\nService ID / Method ID"]
  DET --> STATS["Statistics\n→ IO Graph / Endpoints"]
```
""",

"howto-tcpdump-capture": """
```mermaid
graph LR
  NW["車載Ethernet\n(eth0)"] -->|"tcpdump -i eth0 -w cap.pcap"| ECU["組み込みECU\n(Linux)"]
  ECU -->|SCP転送| PC["診断PC"]
  PC --> WS["Wireshark\n/ tshark 解析"]
```
""",

"howto-ping-ecu": """
```mermaid
flowchart TD
  START["ping 192.168.1.10"] --> RES{応答あり?}
  RES -->|Yes| OK["疎通OK\nL1-L3正常"]
  RES -->|No| L1["ip link show\nリンクUP確認"]
  L1 --> L2{UP?}
  L2 -->|No| PHY["ケーブル/スイッチ確認"]
  L2 -->|Yes| ARP["arp -n\nARPテーブル確認"]
  ARP --> ARP2{MACあり?}
  ARP2 -->|No| SUB["サブネット確認\nip addr show"]
  ARP2 -->|Yes| ICMP["ECU側ICMP無効化\n→ DoIP等で確認"]
```
""",

"howto-doip-connect": """
```mermaid
sequenceDiagram
  participant PC as 診断PC
  participant GW as ゲートウェイECU
  PC->>GW: Vehicle Discovery (UDP 13400 ブロードキャスト)
  GW->>PC: Vehicle Announcement (IP + 論理アドレス)
  PC->>GW: Routing Activation Request (TCP 13400)
  GW->>PC: Routing Activation Response (0x10: 成功)
  PC->>GW: UDS DiagnosticSessionControl (10 03)
  GW->>PC: PositiveResponse (50 03)
```
""",

"howto-uds-dtc": """
```mermaid
sequenceDiagram
  participant PC as 診断ツール
  participant ECU as ゲートウェイECU
  PC->>ECU: 10 03 (拡張診断セッション)
  ECU->>PC: 50 03 ✓
  PC->>ECU: 19 01 08 (DTC件数確認)
  ECU->>PC: 59 01 08 FF 00 05 (5件)
  PC->>ECU: 19 02 08 (全DTC読み出し)
  ECU->>PC: 59 02 08 [DTC×5]
  PC->>ECU: 14 FF FF FF (DTC全クリア)
  ECU->>PC: 54 ✓
```
""",

"howto-tshark-filter": """
```mermaid
graph LR
  PCAP["capture.pcap"] -->|"-Y someip"| F1["SOME/IPパケット"]
  PCAP -->|"-Y doip"| F2["DoIPパケット"]
  PCAP -->|"-z endpoints,ip"| STATS["IPエンドポイント統計"]
  F1 -->|"-T fields -e someip.serviceid"| CSV["ServiceID一覧 (CSV)"]
  STATS --> XLS["Excel分析"]
```
""",

"howto-vlan-check": """
```mermaid
graph LR
  TRUNK["スイッチ\nトランクポート"] -->|VLANタグ付きフレーム| PC["Wireshark"]
  PC -->|"フィルタ: vlan.id == 10"| ADAS["VLAN10 (ADAS)\nトラフィック"]
  PC -->|"フィルタ: vlan.id == 20"| IVI["VLAN20 (IVI)\nトラフィック"]
```
""",

"howto-pcap-analyze": """
```mermaid
flowchart TD
  PCAP["vehicle_capture.pcap"]
  PCAP -->|"tshark -z io,phs"| PROTO["プロトコル分布\n把握"]
  PCAP -->|"ARP opcode==2"| IPTBL["IP/MACテーブル\n再現"]
  PCAP -->|"someip.type==0x01"| SVC["公開サービス\n一覧"]
  PCAP -->|"tcp.analysis.retransmission"| ERR["異常パターン\n検出"]
  PROTO & IPTBL & SVC & ERR --> RPT["解析レポート"]
```
""",
}

def add_diagram(slug: str, diagram: str) -> None:
    path = ARTICLES_DIR / f"{slug}.md"
    if not path.exists():
        print(f"  SKIP (not found): {slug}.md")
        return
    content = path.read_text(encoding="utf-8")
    if "```mermaid" in content:
        print(f"  SKIP (already has diagram): {slug}.md")
        return
    content = content.rstrip() + "\n\n## 図解\n" + diagram.strip() + "\n"
    path.write_text(content, encoding="utf-8")
    print(f"  OK: {slug}.md")

if __name__ == "__main__":
    print(f"Adding diagrams to {len(DIAGRAMS)} articles...")
    for slug, diagram in DIAGRAMS.items():
        add_diagram(slug, diagram)
    print("Done.")
