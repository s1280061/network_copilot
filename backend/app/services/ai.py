"""AI provider abstraction.

Supports OpenAI, Anthropic, and a key-less "mock" mode so the app runs
out of the box. Provider is chosen via AI_PROVIDER in .env.
"""
import httpx

from ..config import get_settings
from ..knowledge import offline_answer

SYSTEM_PROMPT = (
    "あなたはADAS・SDV・車載ネットワーク専門の技術教師です。"
    "Ethernet, TCP/IP, UDP, SOME/IP, CAN, AUTOSAR, ROS2 DDS などを扱います。"
    "初心者向けに分かりやすく説明しながらも、実務での利用例を重視してください。"
    "専門用語には短い補足を添えること。"
    "回答は必ず次の4見出し(Markdownの見出し)で日本語で構成してください:\n"
    "# 一言説明\n# 実務例\n# 関連技術\n# 推奨記事\n"
    "「推奨記事」には、ユーザーが次に読むとよいトピック名を箇条書きで挙げてください。"
)


async def ask_ai(question: str, context: str = "") -> str:
    settings = get_settings()
    provider = settings.ai_provider.lower()
    user_content = question if not context else f"{context}\n\n質問: {question}"

    try:
        if provider == "openai" and settings.openai_api_key:
            return await _ask_openai(settings, user_content)
        if provider == "anthropic" and settings.anthropic_api_key:
            return await _ask_anthropic(settings, user_content)
        if provider == "groq" and settings.groq_api_key:
            return await _ask_groq(settings, user_content)
    except Exception as exc:  # noqa: BLE001 - fall back gracefully
        return (
            f"（AI呼び出しに失敗したためオフライン回答に切替: {exc}）\n\n"
            + offline_answer(question)
        )

    # mock / no key
    return offline_answer(question)


async def _ask_openai(settings, content: str) -> str:
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.openai_api_key}"},
            json={
                "model": settings.openai_model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": content},
                ],
            },
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


async def _ask_groq(settings, content: str) -> str:
    """Groq Cloud API (OpenAI-compatible)."""
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.groq_api_key}"},
            json={
                "model": settings.groq_model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": content},
                ],
            },
        )
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"]


async def _ask_anthropic(settings, content: str) -> str:
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": settings.anthropic_api_key,
                "anthropic-version": "2023-06-01",
            },
            json={
                "model": settings.anthropic_model,
                "max_tokens": 1024,
                "system": SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": content}],
            },
        )
        resp.raise_for_status()
        return resp.json()["content"][0]["text"]
