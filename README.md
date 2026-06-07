# Network Learning Copilot

ADAS・自動運転・SDV・組み込みネットワーク技術を **体系的に学べるAI教師プラットフォーム**。
ChatGPT + Wikipedia + note + 学習ロードマップ を組み合わせた、新人エンジニア向けの学習サービスです。

対象技術: Ethernet / TCP/IP / UDP / SOME/IP / CAN / AUTOSAR / ROS2 DDS / SDV など。

---

## 主な機能

| 機能 | 内容 |
|------|------|
| 📚 学習ロードマップ | Level 1〜5 をツリー表示。各項目に学習済みチェック、ヘッダーに進捗バー |
| 📖 用語集 / 記事 | 17記事をMarkdownで管理。概要 / なぜ必要か / 自動運転での利用例 / 関連用語 / 次に学ぶべき内容 |
| 🔗 内部リンク | 記事内の用語(`[[slug]]`)をクリックして関連記事へ遷移(Wikipedia風の回遊) |
| 💬 AIチャット | 「一言説明 / 詳細解説 / 自動運転での利用例 / 関連知識 / 次に学ぶべきこと」の5見出しで回答。回答中の用語から記事を推薦 |
| 📂 PCAP解析 | Scapyでプロトコル抽出。検出プロトコルから関連学習記事を推薦(例: UDP検出→UDP/TCP/Socket記事) |
| ⭐ お気に入り | 記事を保存 |
| 📝 学習履歴 | 閲覧記事・AIへの質問・PCAP解析を記録 |
| 🧭 学習支援パネル | 右カラムに関連用語・推奨記事・次に学ぶべき項目をコンテキスト連動表示 |
| 🏠 note風ホーム | カテゴリ別(Ethernet/TCP-IP/PCAP/SOME-IP/AUTOSAR/SDV)の記事カード(難易度・閲覧数・更新日)|
| 🔥 人気ランキング | 閲覧数を集計してTOP10表示 |
| ✨ あなたへのおすすめ | 記事閲覧時に「内部リンク+タグ+RAG意味類似」で関連記事を推薦 |
| 📊 ダッシュボード | 学習済み数・学習率・カテゴリ別進捗をレーダーチャート/棒グラフで可視化 |
| 🔎 意味検索(RAG) | ChromaDB + ローカル多言語Embeddingで記事を意味検索 |
| 📚 AI回答の引用 | チャット回答にRAGで見つけた「参考記事」リンクを表示(回答コンテキストにも注入)|

> AIは **Groq Cloud API**(OpenAI互換)に対応。`AI_PROVIDER=mock` ならキー無しでも簡易回答で動作します。
> RAG(意味検索・推薦)は **ChromaDB + fastembed(多言語MiniLM, ONNX, torch不要)** で実装。依存未導入でもキーワード検索・タグ推薦に**自動フォールバック**します。

---

## 画面構成(3カラム)

```
┌────────────────────────────────────────────────────────────┐
│ Header: 📡 タイトル                    学習進捗 ▓▓▓░░ 42%   │
├──────────┬──────────────────────────────┬───────────────────┤
│ 左:ナビ  │ 中央: コンテンツ             │ 右: 学習支援パネル│
│ 📚📖💬📂⭐📝│ 記事 / チャット / PCAP結果  │ 関連/推奨/次に学ぶ│
└──────────┴──────────────────────────────┴───────────────────┘
```

---

## ディレクトリ構成

```
network_copilot/
├── README.md
├── backend/                       # FastAPI + Scapy
│   ├── requirements.txt
│   ├── .env / .env.example
│   └── app/
│       ├── main.py                # ルーター集約 + health
│       ├── config.py / db.py      # 設定 / SQLite(履歴・お気に入り・進捗)
│       ├── knowledge.py           # オフライン回答(mock)
│       ├── routers/               # 機能別エンドポイント
│       │   ├── content.py         #   /api/roadmap, /api/articles[/{slug}]
│       │   ├── chat.py            #   /api/chat
│       │   ├── pcap.py            #   /api/pcap (+記事推薦)
│       │   └── progress.py        #   /api/favorites, /api/progress, /api/history
│       ├── content/               # 学習コンテンツ(データ)
│       │   ├── roadmap.json
│       │   └── articles/*.md      #   17記事(frontmatter + [[内部リンク]])
│       ├── services/
│       │   ├── ai.py              #   groq / openai / anthropic / mock
│       │   ├── content.py         #   記事ロード・Markdown→HTML・[[link]]解決
│       │   └── recommend.py       #   プロトコル→記事推薦
│       └── analyzers/pcap.py      # Scapy解析(将来 can.py / someip.py)
└── frontend/                      # Next.js (App Router) + TS + Tailwind
    ├── app/
    │   ├── layout.tsx             # 3カラムの土台
    │   ├── page.tsx               # / → 学習ロードマップ
    │   ├── glossary/page.tsx      # 記事一覧
    │   ├── glossary/[slug]/page.tsx  # 記事ページ(内部リンク遷移)
    │   ├── chat/ pcap/ favorites/ history/  # 各ビュー
    │   └── globals.css
    ├── components/
    │   ├── layout/{Header,SidebarNav,StudyPanel}.tsx
    │   ├── roadmap/RoadmapTree.tsx
    │   ├── article/ArticleView.tsx
    │   └── Mermaid.tsx
    └── lib/{api.ts, types.ts, study-context.tsx}
```

---

## ローカル起動手順 (Windows / PowerShell)

### 1. バックエンド (FastAPI) — ポート 8081

```powershell
cd C:\Users\s1280\Desktop\network_copilot\backend

python -m venv .venv            # 初回のみ
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt # 初回のみ(markdown / pyyaml を含む)

Copy-Item .env.example .env     # 初回のみ(Groqキー等を設定)

uvicorn app.main:app --reload --port 8081
```

- APIドキュメント: http://localhost:8081/docs
- ヘルスチェック: http://localhost:8081/api/health

### 2. フロントエンド (Next.js) — ポート 3000

別ターミナルで:

```powershell
cd C:\Users\s1280\Desktop\network_copilot\frontend

npm install                       # 初回のみ
Copy-Item .env.local.example .env.local   # 既定で 8081 を参照

npm run dev
```

ブラウザで http://localhost:3000 を開く。

> **ポートについて**: フロントは `.env.local` の `NEXT_PUBLIC_API_BASE` でバックエンドURLを参照します(既定 `http://localhost:8081`)。
> バックエンドのポートを変える場合は両方を合わせてください。`WinError 10013/10048` が出る場合はそのポートが使用中/予約済みです。別ポートに変更してください。

---

## AI(Groq)の設定

`backend/.env`:

```
AI_PROVIDER=groq
GROQ_API_KEY=（あなたのキー）
GROQ_MODEL=llama-3.3-70b-versatile
```

- 他プロバイダ: `AI_PROVIDER` を `openai` / `anthropic` / `mock` に切替可能。
- モデル変更例: `openai/gpt-oss-120b`, `openai/gpt-oss-20b` など。
- ⚠️ APIキーが漏れた場合は https://console.groq.com で再発行してください。

---

## 使い方

1. **学習ロードマップ**(ホーム)で Level 1 から順に項目をクリック → 記事を読む。
2. 記事末尾や本文の **用語リンク** をクリックして関連記事へ回遊。読んだら「✓ 学習済み」。
3. 分からないことは **AIチャット** で質問(回答から関連記事を推薦)。
4. 実データは **PCAP解析** にアップロード(検出プロトコルから記事を推薦)。
5. **お気に入り / 学習履歴** で振り返り。

---

## 学習コンテンツの追加方法

`backend/app/content/articles/` に Markdown を追加するだけです:

```markdown
---
slug: tsn
title: TSN
level: 5
related: [ethernet, adas-comm]
next: []
tags: [automotive]
---

## 概要
本文中で [[ethernet]] のように書くと内部リンクになります。
```

`roadmap.json` の該当レベルの `items` に slug を追加すればロードマップにも並びます。

### 自動Embedding(RAG)ワークフロー

記事を追加・編集して **バックエンドを再起動するだけ** で、変更分だけ自動でEmbedding生成 → ChromaDB登録されます(起動時に内容ハッシュで差分検出)。手動実行も可能:

```powershell
cd backend
python -m app.reindex          # 差分のみ再インデックス
python -m app.reindex --force  # 全件再インデックス
```

- `category` 未指定時は slug→カテゴリの既定マッピング、`difficulty` 未指定時は `level` から自動設定、`updated` 未指定時はファイル更新日を使用。
- RAG関連の生成物(`backend/data/chroma/`, `rag_index.json`)は `.gitignore` 済み。初回のEmbeddingモデル(約0.22GB)は自動ダウンロードされます。

---

## 将来拡張

- **CAN / SOME-IP の実解析**: `analyzers/` に `can.py` / `someip.py` を追加(`pcap.py` と同じI/F)。
- **AUTOSAR / ROS2 DDS の記事拡充**: `content/articles/` に追記。
- **Wireshark連携**: tshark を呼ぶアナライザを追加可能。
- **全文検索 / 学習進捗の可視化強化**。

---

## デプロイ

このアプリは **フロント(Next.js)** と **バックエンド(FastAPI + Scapy + ChromaDB)** の2層構成です。
バックエンドはScapy・ChromaDB・MLモデルのため、Vercelのサーバーレスでは動きません。
**フロント=Vercel / バックエンド=Render** の分離構成を推奨します。

### バックエンド(Render)
1. https://render.com で GitHub リポジトリを連携(`render.yaml` を自動検出)。
2. 環境変数を設定:
   - `GROQ_API_KEY` = あなたのGroqキー
   - `FRONTEND_ORIGIN` = VercelのURL(例 `https://network-copilot.vercel.app`)
3. デプロイ後の URL(例 `https://network-copilot-api.onrender.com`)を控える。

### フロントエンド(Vercel)
1. https://vercel.com で同じリポジトリをインポート。
2. **Root Directory を `frontend` に設定**(モノレポのため必須)。
3. 環境変数 `NEXT_PUBLIC_API_BASE` = バックエンドのURL(上で控えたRenderのURL)。
4. Deploy。フレームワークは Next.js が自動検出されます。

> `*.vercel.app` はバックエンドのCORSで許可済み。独自ドメインを使う場合は `FRONTEND_ORIGIN` に設定してください。
> RenderのEmbeddingモデル初回DLでメモリを使うため、無料枠で不足する場合は有料インスタンスを検討してください。

---

## 技術スタック

- Frontend: Next.js 14 (App Router) / TypeScript / TailwindCSS / Mermaid
- Backend: FastAPI / Uvicorn
- Packet解析: Scapy
- コンテンツ: Markdown(frontmatter)
- AI: Groq / OpenAI / Anthropic / mock
- DB: SQLite
