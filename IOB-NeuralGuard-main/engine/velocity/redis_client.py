import redis.asyncio as redis
from config.settings import settings

_pool = redis.ConnectionPool(
    host=settings.redis_host,
    port=settings.redis_port,
    password=settings.redis_password,
    max_connections=20,
    decode_responses=True
)

_client = redis.Redis(connection_pool=_pool)

async def get_redis() -> redis.Redis:
    return _client

async def ping() -> bool:
    try:
        return await _client.ping()
    except Exception:
        return False
