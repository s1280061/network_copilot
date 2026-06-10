---
slug: fastapi
title: FastAPI（高速WebAPI開発）
level: 2
category: Python
related: [python-basics, pandas, llm]
next: []
tags: [fastapi, python, api, web, backend]
---

## 概要
FastAPIはPythonの型ヒントを活かした高速なWebAPIフレームワークです。自動的なOpenAPIドキュメント生成・型バリデーション・非同期処理をサポートし、機械学習モデルや分析ツールのAPIサーバーとして最も人気があります。

## なぜ FastAPI か

| | Flask | Django REST | FastAPI |
|---|---|---|---|
| 速度 | 普通 | 普通 | **高速（Starlette/uvicorn）** |
| 型バリデーション | 手動 | 手動 | **自動（Pydantic）** |
| APIドキュメント | 手動 | 手動 | **自動生成（Swagger UI）** |
| 非同期 | △ | △ | **ネイティブ対応** |
| 学習コスト | 低い | 高い | 低い |

## 基本的なAPI

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn

app = FastAPI(
    title="Network Copilot API",
    description="車載ネットワーク分析ツール",
    version="1.0.0",
)

# Pydantic でリクエスト/レスポンスの型を定義
class PacketSummary(BaseModel):
    src_ip:    str
    dst_ip:    str
    protocol:  str
    count:     int
    bytes_total: int

class AnalysisResult(BaseModel):
    total_packets: int
    duration_sec:  float
    top_flows:     list[PacketSummary]
    anomaly_count: int = 0

# GETエンドポイント
@app.get("/api/health")
def health_check():
    return {"status": "ok"}

# パスパラメータ
@app.get("/api/articles/{slug}", summary="記事を取得")
def get_article(slug: str):
    articles = {"ethernet": {"title": "Ethernet", "category": "Ethernet"}}
    if slug not in articles:
        raise HTTPException(status_code=404, detail=f"Article '{slug}' not found")
    return articles[slug]

# クエリパラメータ
@app.get("/api/articles", summary="記事一覧")
def list_articles(
    category: Optional[str] = None,
    limit:    int = 20,
    offset:   int = 0,
):
    return {"category": category, "limit": limit, "offset": offset}
```

## POSTエンドポイントとバリデーション

```python
from pydantic import BaseModel, Field, validator

class PcapUploadRequest(BaseModel):
    filename: str       = Field(..., min_length=1, max_length=255)
    max_packets: int    = Field(default=10000, ge=1, le=100000)
    filter_expr: str    = Field(default="", description="BPFフィルタ式")

    @validator("filename")
    def filename_must_be_pcap(cls, v):
        if not v.endswith((".pcap", ".pcapng")):
            raise ValueError("PCAPファイルのみ対応（.pcap / .pcapng）")
        return v

class ChatRequest(BaseModel):
    question: str  = Field(..., min_length=1, max_length=2000)
    model:    str  = Field(default="claude-opus-4-8")

class ChatResponse(BaseModel):
    answer:  str
    sources: list[dict]
    tokens:  int

@app.post("/api/chat", response_model=ChatResponse, summary="AIチャット")
async def chat(req: ChatRequest):
    # 実際の処理（例: LLMを呼ぶ）
    return ChatResponse(
        answer=f"「{req.question}」への回答です。",
        sources=[],
        tokens=len(req.question),
    )
```

## ファイルアップロード

```python
from fastapi import UploadFile, File, Form
import tempfile
import os

@app.post("/api/pcap/upload", summary="PCAPファイルをアップロード")
async def upload_pcap(
    file:        UploadFile = File(...),
    max_packets: int        = Form(default=10000),
):
    if not file.filename.endswith((".pcap", ".pcapng")):
        raise HTTPException(status_code=400, detail="PCAPファイルのみ対応")

    # 一時ファイルに保存して処理
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pcap") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name

    try:
        # ここで解析処理
        result = {"filename": file.filename, "size_bytes": len(content)}
    finally:
        os.unlink(tmp_path)

    return result
```

## 非同期処理とバックグラウンドタスク

```python
from fastapi import BackgroundTasks
import asyncio
import httpx

# 非同期エンドポイント（I/O待ちがあるならasyncにする）
@app.get("/api/external")
async def fetch_external():
    async with httpx.AsyncClient() as client:
        r = await client.get("https://api.example.com/data", timeout=5.0)
        return r.json()

# バックグラウンドタスク（レスポンスを返しながら処理続行）
def send_notification(email: str, message: str):
    print(f"メール送信: {email} → {message}")   # 実際はSMTPなど

@app.post("/api/analyze")
async def analyze(background_tasks: BackgroundTasks, slug: str):
    background_tasks.add_task(send_notification, "admin@example.com",
                              f"解析完了: {slug}")
    return {"status": "processing", "slug": slug}
```

## 依存性注入（Depends）

```python
from fastapi import Depends
from functools import lru_cache

class Settings:
    app_name: str = "Network Copilot"
    api_key:  str = "secret"
    debug:    bool = False

@lru_cache
def get_settings() -> Settings:
    return Settings()

@app.get("/api/settings")
def read_settings(settings: Settings = Depends(get_settings)):
    return {"app": settings.app_name, "debug": settings.debug}

# DB接続の依存性注入例
def get_db():
    db = {"conn": "sqlite:///app.db"}
    try:
        yield db
    finally:
        pass   # クローズ処理

@app.get("/api/data")
def get_data(db: dict = Depends(get_db)):
    return {"db": db["conn"]}
```

## ミドルウェアとCORS

```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
import time

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://your-app.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# リクエストのログとタイミング
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

class TimingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        t0       = time.time()
        response = await call_next(request)
        elapsed  = time.time() - t0
        response.headers["X-Process-Time"] = f"{elapsed:.3f}"
        print(f"{request.method} {request.url.path} → {response.status_code} ({elapsed*1000:.1f}ms)")
        return response

app.add_middleware(TimingMiddleware)
```

## サーバーの起動

```bash
# 開発サーバー（ホットリロード）
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 本番（複数ワーカー）
uvicorn main:app --workers 4 --host 0.0.0.0 --port 8000
```

`http://localhost:8000/docs` で Swagger UI が自動生成されます。
