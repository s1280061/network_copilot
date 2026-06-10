# 記事サムネイル画像

このフォルダに記事のサムネイル画像を置くと、トップページのカードと
記事詳細ページのヘッダーに note のように画像が表示されます。

## 命名規則

ファイル名を **記事のスラッグ（slug）** に合わせてください。
拡張子は `.png` / `.jpg` / `.jpeg` / `.webp` のいずれかが使えます。

例:
- `ethernet.png`
- `tcp.jpg`
- `some-ip.webp`

画像が無いスラッグは、カテゴリ別のカラーバナー（アイコン付き）に
自動でフォールバックします。

## 推奨サイズ

横長（おおよそ 1200 x 630 など、note のヘッダー比率）を推奨します。
カードでは高さ 96px、詳細ページでは高さ 192〜256px に
`object-cover` でトリミング表示されます。

## スラッグ一覧

```
adas-comm
arp
autosar
can
can-fd
communication-basics
dhcp
dns
doip
ethernet
icmp
ip
mac-address
osi
pcap
port
ros2-dds
sdv
socket
some-ip
subnet
tcp
tcpdump
tsn
tshark
udp
vlan
wireshark
```
