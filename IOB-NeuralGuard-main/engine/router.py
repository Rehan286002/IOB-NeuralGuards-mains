import time
import asyncio
from fastapi import APIRouter
from ingestion.schemas import Transaction
from engine.velocity.engine import check_velocity
from engine.velocity.redis_client import ping
from engine.voice.analyzer import analyze_voice
from core.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

@router.get("/health")
async def health_check():
    redis_status = await ping()
    return {"status": "ok", "redis": redis_status}

@router.post("/analyze")
async def analyze_transaction(txn: Transaction):
    start_time = time.perf_counter()
    reasons = []

    try:
        # 1. Velocity Check (Fast Path)
        velocity_result = await check_velocity(txn.sender_upi)

        if velocity_result["decision"] == "BLOCK":
            reasons.append(velocity_result["reason"])
            latency = (time.perf_counter() - start_time) * 1000
            return {"txn_id": txn.txn_id, "decision": "BLOCK", "reasons": reasons, "latency_ms": round(latency, 2)}

        # 2. Voice Analysis (Slow Path - only if applicable)
        if txn.channel == "VOICE_123PAY" and txn.audio_ref:
            loop = asyncio.get_running_loop()
            try:
                voice_result = await asyncio.wait_for(
                    loop.run_in_executor(None, analyze_voice, txn.audio_ref),
                    timeout=0.15  # 150ms
                )
                if voice_result and voice_result["decision"] == "BLOCK":
                    reasons.append(voice_result["reason"])
                    latency = (time.perf_counter() - start_time) * 1000
                    return {"txn_id": txn.txn_id, "decision": "BLOCK", "reasons": reasons, "latency_ms": round(latency, 2)}
            except asyncio.TimeoutError:
                logger.warning(f"Voice analysis timed out for txn {txn.txn_id} — FAIL OPEN")
            except Exception as e:
                logger.error(f"Voice analysis error: {e}")

        latency = (time.perf_counter() - start_time) * 1000
        return {"txn_id": txn.txn_id, "decision": "ALLOW", "reasons": [], "latency_ms": round(latency, 2)}

    except Exception as e:
        logger.error(f"Engine failure: {e}")
        return {"txn_id": txn.txn_id, "decision": "ALLOW", "error": "internal_error", "latency_ms": 0}
