from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: Optional[str] = None

    # Neo4j
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "neuraguard123"

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_topic: str = "upi-transactions"

    # App
    app_env: str = "development"
    log_level: str = "INFO"
    circuit_breaker_timeout_ms: int = 150
    max_txn_per_min: int = 5

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Singleton — import this everywhere, never re-instantiate
settings = Settings()
