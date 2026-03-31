from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from engine.velocity.redis_client import get_redis
from core.logger import get_logger

logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("NeuralGuard Engine Started")
    redis = await get_redis()
    try:
        await redis.ping()
        logger.info("Redis Connected")
    except Exception as e:
        logger.error(f"Redis Connection Failed: {e}")
    yield
    logger.info("Shutting down NeuralGuard Engine...")
    await redis.aclose()

app = FastAPI(title="IOB-NeuralGuard-Core", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from engine.router import router
app.include_router(router)
