import asyncio
import functools
from core.logger import get_logger

logger = get_logger(__name__)

def with_timeout(timeout_ms: int, fallback=None):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout_ms / 1000
                )
            except asyncio.TimeoutError:
                logger.warning(f"Circuit breaker triggered on {func.__name__} after {timeout_ms}ms — FAIL OPEN")
                return fallback
        return wrapper
    return decorator
