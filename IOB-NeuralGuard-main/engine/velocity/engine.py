from datetime import datetime
from config.settings import settings
from core.logger import get_logger
from engine.velocity.redis_client import get_redis

logger = get_logger(__name__)

async def check_velocity(sender_upi: str) -> dict:
    current_minute = datetime.utcnow().strftime("%Y%m%d%H%M")
    key = f"ng:v1:velocity:{sender_upi}:{current_minute}"
    redis_client = await get_redis()
    try:
        async with redis_client.pipeline(transaction=True) as pipe:
            pipe.incr(key)
            pipe.expire(key, 60)
            results = await pipe.execute()
            count = results[0]
        if count > settings.max_txn_per_min:
            logger.warning(f"Velocity limit reached for {sender_upi}: {count}")
            return {"decision": "BLOCK", "reason": "velocity_exceeded", "count": count}
        return {"decision": "ALLOW", "count": count}
    except Exception as e:
        logger.error(f"Velocity check failed for {sender_upi}: {str(e)}")
        return {"decision": "ALLOW", "error": "velocity_engine_unavailable"}
