import json
import tempfile
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from ..analyzers.pcap import analyze_pcap
from ..services.ai import ask_ai
from ..services.recommend import recommend_from_protocols, recommend_note
from ..db import save_pcap

router = APIRouter(prefix="/api", tags=["pcap"])


@router.post("/pcap")
async def pcap(file: UploadFile = File(...)):
    suffix = Path(file.filename or "upload.pcap").suffix or ".pcap"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        result = analyze_pcap(tmp_path)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(status_code=400, detail=f"解析に失敗しました: {exc}")
    finally:
        Path(tmp_path).unlink(missing_ok=True)

    # Phase 3: link analysis -> learning articles
    result["recommendations"] = recommend_from_protocols(result["protocols"])
    result["recommend_note"] = recommend_note(result["protocols"])

    # Learning explanation from AI
    context = (
        "次はPCAP解析結果のサマリです。これを初心者向けに学習解説してください。\n"
        + json.dumps(
            {"protocols": result["protocols"], "ports": result["ports"][:5]},
            ensure_ascii=False,
        )
    )
    result["explanation"] = await ask_ai("このPCAPから何が学べますか?", context)

    save_pcap(
        file.filename or "upload.pcap",
        json.dumps(result["protocols"], ensure_ascii=False),
    )
    return result
