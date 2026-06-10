---
slug: langchain
title: LangChain（LLMアプリ開発フレームワーク）
level: 3
category: GenAI
related: [llm, rag, prompt-engineering, fastapi]
next: []
tags: [langchain, llm, rag, python, langchain, openai, claude]
---

## 概要
LangChainはLLMを使ったアプリケーション開発を簡単にするPythonフレームワークです。プロンプト管理・チェーン処理・RAG（検索拡張生成）・エージェント・ツール呼び出しを統一したAPIで扱えます。OpenAI・Anthropic・ローカルLLMなど多様なモデルに対応します。

## 基本セットアップ

```python
# pip install langchain langchain-anthropic langchain-openai
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Anthropic Claude
llm = ChatAnthropic(
    model="claude-opus-4-8",
    temperature=0.7,
    max_tokens=1024,
)

# シンプルな呼び出し
response = llm.invoke("CANバスとは何ですか？一文で説明してください。")
print(response.content)

# メッセージリストで呼び出し
messages = [
    SystemMessage(content="あなたは車載ネットワークの専門家です。"),
    HumanMessage(content="SOME/IPとは何ですか？"),
]
response = llm.invoke(messages)
print(response.content)
```

## プロンプトテンプレート

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# テンプレートの定義
prompt = ChatPromptTemplate.from_messages([
    ("system", "あなたは{domain}の専門家です。{tone}で回答してください。"),
    ("human",  "{question}"),
])

# LCELチェーン（| 演算子でパイプライン構成）
chain = prompt | llm | StrOutputParser()

answer = chain.invoke({
    "domain":   "車載ネットワーク",
    "tone":     "技術者向けに簡潔",
    "question": "DoIPとは何ですか？",
})
print(answer)
```

## 会話履歴の管理

```python
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

store: dict[str, InMemoryChatMessageHistory] = {}

def get_history(session_id: str) -> InMemoryChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

prompt_with_history = ChatPromptTemplate.from_messages([
    ("system", "あなたは車載ネットワークのアシスタントです。"),
    MessagesPlaceholder("history"),
    ("human", "{input}"),
])

chain_with_history = RunnableWithMessageHistory(
    prompt_with_history | llm | StrOutputParser(),
    get_history,
    input_messages_key="input",
    history_messages_key="history",
)

session = {"configurable": {"session_id": "user_001"}}
r1 = chain_with_history.invoke({"input": "CAN FDとは何ですか？"}, config=session)
r2 = chain_with_history.invoke({"input": "先ほどの話の続きで、用途は？"}, config=session)
print(r1)
print(r2)
```

## RAGパイプラインの構築

```python
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings  import HuggingFaceEmbeddings
from langchain_core.documents        import Document
from langchain.chains                import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain

# ドキュメントの準備
docs = [
    Document(page_content="CAN（Controller Area Network）は車載ネットワークプロトコル。最大1Mbps。", metadata={"source": "can.md"}),
    Document(page_content="SOME/IPはEthernet上でのSOA通信プロトコル。BMW・Mercedes採用。",        metadata={"source": "some-ip.md"}),
    Document(page_content="DoIPは診断通信をEthernetで行うプロトコル。ISO 13400準拠。",            metadata={"source": "doip.md"}),
]

# ベクトルストアの作成
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
vectorstore = FAISS.from_documents(docs, embeddings)
retriever   = vectorstore.as_retriever(search_kwargs={"k": 2})

# RAGチェーンの組み立て
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "以下のコンテキストを使って質問に答えてください。\n\nコンテキスト:\n{context}"),
    ("human",  "{input}"),
])
doc_chain = create_stuff_documents_chain(llm, qa_prompt)
rag_chain = create_retrieval_chain(retriever, doc_chain)

result = rag_chain.invoke({"input": "診断通信をEthernetで行うには？"})
print(result["answer"])
print("参照ソース:", [d.metadata["source"] for d in result["context"]])
```

## ツール呼び出し（Function Calling）

```python
from langchain_core.tools import tool
from langchain.agents import create_tool_calling_agent, AgentExecutor

@tool
def get_protocol_info(protocol_name: str) -> str:
    """車載プロトコルの技術情報を返す"""
    db = {
        "CAN":    "最大1Mbps, 11/29bitID, 車体系ECU制御に使用",
        "SOME/IP":"Ethernet上SOA, サービス検出(SD), BMW/Daimler採用",
        "DoIP":   "ISO 13400, TCP/UDP, 診断通信をEthernetで実施",
    }
    return db.get(protocol_name.upper(), "プロトコル情報が見つかりません")

@tool
def calculate_bus_load(message_rate: float, payload_bytes: int, bitrate_kbps: float = 500) -> str:
    """CANバス負荷率を計算する"""
    bits_per_frame = 47 + payload_bytes * 8    # CANフレームのオーバーヘッド込み
    load = (message_rate * bits_per_frame) / (bitrate_kbps * 1000) * 100
    return f"バス負荷率: {load:.1f}%（{bitrate_kbps}kbps時）"

tools = [get_protocol_info, calculate_bus_load]

agent_prompt = ChatPromptTemplate.from_messages([
    ("system", "あなたは車載ネットワークのアシスタントです。ツールを使って正確に回答してください。"),
    ("human", "{input}"),
    MessagesPlaceholder("agent_scratchpad"),
])

agent = create_tool_calling_agent(llm, tools, agent_prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

result = executor.invoke({"input": "SOME/IPの説明と、100msg/sで8バイトのCANバス負荷率を教えて"})
print(result["output"])
```

## ストリーミングレスポンス

```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse

app = FastAPI()

@app.get("/stream")
async def stream_answer(question: str):
    async def generator():
        async for chunk in llm.astream(question):
            yield chunk.content

    return StreamingResponse(generator(), media_type="text/plain")
```
