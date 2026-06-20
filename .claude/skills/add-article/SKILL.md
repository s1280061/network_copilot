---
name: add-article
description: >
  network_copilot 学習プラットフォームに記事を追加・編集するときの一連の手順。
  「記事を追加して」「〇〇とはの記事を作って」「ハウツー記事を足して」「図解を入れて」
  「重要なところを太字に」「サムネ画像を付けて」「Vercelに反映して」などと言われたら
  必ずこのスキルを使うこと。記事の markdown 作成だけでなく、カテゴリ登録・ロードマップ更新・
  静的コンテンツ再生成・サムネ生成・ビルド・git push までの一連のパイプラインを取りこぼし
  なく実行するためのもの。記事まわりの作業で「片方だけ更新して反映漏れ」が起きやすいので、
  単一ファイルの編集に見えても全体の手順を確認する。
---

# network_copilot 記事追加パイプライン

このリポジトリ（`C:\Users\s1280\Desktop\network_copilot`）は、ADAS/車載ネットワーク等を
学ぶ学習サイト。FastAPI バックエンド（記事の真実のソース）と Next.js フロントエンド
（Vercel デプロイ）の二層構成で、**Vercel は静的モードで動く**ため、記事を足したら
`static-content.json` を必ず再生成しないと本番に反映されない。ここが一番の落とし穴。

## 全体の流れ

記事を1本でも追加・変更したら、原則として下の手順を**通しで**実行する。
「md を1つ足すだけ」に見えても、③〜⑤を飛ばすと本番サイトに出ない。

1. 記事 markdown を作成（frontmatter 付き）
2. カテゴリを登録（必要なら）
3. ロードマップに配置（必要なら）
4. 静的コンテンツを再生成
5. サムネ画像を用意
6. ビルド確認 → git push（Vercel 自動デプロイ）

---

## ① 記事 markdown の作成

場所: `backend/app/content/articles/<slug>.md`

frontmatter のスキーマ（既存記事に合わせる）:

```markdown
---
slug: ipv4-ipv6
title: IPv4 と IPv6
level: 2
category: TCP/IP
tags: [ip, tcp-ip, addressing]
related: [ip, subnet, dhcp]
next: [tcp, udp]
---

## 概要
本文...
```

- `slug` はファイル名と一致させる（小文字・ハイフン区切り）。
- `level` は学習段階（1=基礎 〜 7=実践ノウハウ）。`difficulty` は level から自動。
- `related` / `next` は他記事の slug。`next` の逆向きが自動的に前提知識(prereq)になる。
- 本文中の `[[slug]]` は用語リンクに自動変換される。リンクは積極的に張る。
- 見出しは `##`（H2）で区切る。RAG はこの H2 単位でチャンク化する。

### 図解（Mermaid）

「図解があると有難い」系の依頼では、本文末に `## 図解` を足して Mermaid を入れる。
フロントの `ArticleView.tsx` が ```` ```mermaid ```` ブロックを検出して SVG に変換する。
記事のテーマに合った図を選ぶ:

- プロトコルの手順 → `sequenceDiagram`
- 構成・階層・分類 → `graph TD` / `graph LR`
- 判断フロー → `flowchart TD`

複数記事へ一括で図を入れるなら `backend/add_diagrams.py` のパターンを流用する
（slug → Mermaid 文字列の辞書を作り、`## 図解` を append。既に `​```mermaid` があればスキップ）。

### 重要キーワードの太字化

「大事なところを太字に」と言われたら、規格名・数値・コマンドオプション・専門用語を
`**...**` で囲む。複数記事へ一括適用するときは `backend/bold_keywords.py` を流用
（slug → [(語, 太字版)] の辞書。コードブロックと見出し行は除外し、既に太字のものはスキップ）。

> ⚠️ 一括太字化の落とし穴: **frontmatter（先頭の `--- ... ---` 区間）は絶対に太字化しない**。
> 過去に `slug:` や `title:` 内のキーワードまで `**` で囲んでしまい、`slug: howto-**ping**-ecu`
> のように slug が壊れて本番URLが不正になった事故がある。一括置換は必ず frontmatter を
> 除外して body だけに適用すること。万一壊したら `backend/fix_frontmatter_bold.py`
> （frontmatter区間の `**` を一掃する）で復旧できる。

---

## ② カテゴリ登録

`backend/app/services/content.py` の2か所:

- `CATEGORIES` リスト（ホーム画面の大分類。新カテゴリを足すならここに追加）
- `_CATEGORY_MAP` 辞書（`slug -> カテゴリ名`）

frontmatter に `category:` を書けば `_CATEGORY_MAP` 未登録でもそちらが優先される。
ただし既存記事は `_CATEGORY_MAP` で管理しているので、それに倣って追記しておくと一貫する。

---

## ③ ロードマップ配置

`backend/app/content/roadmap.json` の該当レベルの `items` 配列に slug を追加する。
記事の `level` に対応するレベルへ入れるのが自然。ロードマップに載せない記事もあってよい。

---

## ④ 静的コンテンツ再生成（最重要・忘れやすい）

```powershell
cd C:\Users\s1280\Desktop\network_copilot\backend
python -m app.gen_static
```

→ `frontend/lib/static-content.json`（全記事の HTML・推薦・ロードマップ等）を再生成。
出力に `wrote ... (N articles)` と件数が出るので、想定どおり増えているか確認する。

依存が無いと `ModuleNotFoundError: markdown` 等が出る。その場合:
`pip install markdown pyyaml -q`

---

## ⑤ サムネ画像

記事カードと記事ヘッダは `frontend/public/thumbnails/<slug>.jpg` を表示する。
画像が無い記事は `Thumbnail.tsx` が
`/thumbnails/{slug}.{png|jpg|jpeg|webp}` → Pollinations AI生成 → 絵文字 の順でフォールバックする。

本番では「その場生成」だと初回 5〜15 秒の遅延が出るため、**事前生成して保存**するのが推奨。
不足分だけを一括生成するスクリプトがある:

```powershell
cd C:\Users\s1280\Desktop\network_copilot\backend
python gen_thumbnails.py
```

- `static-content.json` から slug/title/category を読み、画像が無い記事だけ Pollinations で生成して
  `frontend/public/thumbnails/<slug>.jpg` に保存する（並列4・リトライ付き）。
- カテゴリごとに画風プロンプトを変えている。失敗 slug は再実行すれば続きから埋まる。
- だから ⑤ は必ず ④ の後に実行する（新記事が static に入っていないと対象に含まれない）。

`next/image` で外部URLを直接使う場合は `next.config.mjs` の `images.remotePatterns` に
`image.pollinations.ai` を登録しておく必要がある（登録済み）。

---

## ⑥ ビルド確認 → デプロイ

```powershell
cd C:\Users\s1280\Desktop\network_copilot\frontend
npm run build
```

`✓ Compiled successfully` を確認（型エラーや依存不足はここで出る）。問題なければ:

```powershell
cd C:\Users\s1280\Desktop\network_copilot
git add -A
git commit -m "<変更内容>

Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>"
git push origin main
```

main への push で **Vercel が自動デプロイ**する。push 時に
`! [rejected] ... (fetch first)` が出たら、リモートに別の変更があるので
`git pull origin main` でマージ（コンフリクトは解消）してから push し直す。

---

## チェックリスト（最後に確認）

- [ ] `<slug>.md` を作成し frontmatter を埋めた
- [ ] 必要なら `_CATEGORY_MAP` / `CATEGORIES` を更新
- [ ] 必要なら `roadmap.json` に追加
- [ ] `python -m app.gen_static` を実行し件数が増えた
- [ ] サムネ（`gen_thumbnails.py` か手動配置）
- [ ] `npm run build` が成功
- [ ] commit して `git push origin main`（= Vercel 反映）

## AIチャットについて（参考）

チャットは `frontend/app/api/chat/route.ts`（Next.js API Route）で動く。
**Groq API**（`llama-3.3-70b-versatile`、OpenAI互換エンドポイント）を呼び、
`static-content.json` から関連記事を検索して RAG コンテキストに添える。
回答は「一言説明 / 詳細解説 / 自動運転での利用例 / 関連知識 / 次に学ぶべきこと」の5見出し構成。
Vercel 環境変数 `GROQ_API_KEY` が必要。
