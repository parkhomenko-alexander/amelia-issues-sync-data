from enum import Enum

from loguru import logger
from redis import RedisError, StrictRedis

from config import config


class CachePrefixes(Enum):
    BUILDINGS_ROOMS_INFO = "BUILDINGS_INFO"
    TASKS_INFO = "TASKS_INFO"


class RedisManager:
    def __init__(self):
        self.redis_client: StrictRedis = StrictRedis(
            host=config.REDIS_HOST, 
            port=config.REDIS_PORT, 
            db=config.REDIS_DB
        )

    def get_client(self):
        return self.redis_client

    def close(self):
        self.redis_client.close()

    async def set_cache(self, prefix: CachePrefixes, key: str | None = None,  val: str = ""):
        try:
            if key:
                full_key = f"{prefix.value}:{key}"
            else:
                full_key = prefix.value

            logger.info(f"Cache was updated for prefix: {full_key}")
            with self.redis_client.pipeline() as pipe:
                pipe.set(full_key, val)
                pipe.execute()
        except RedisError as e:
            logger.error("Failed update cache for preifx '{prefix}': {e}")

    async def get_cache(self, prefix: CachePrefixes, key: str | None = None) -> str | None:
        try:
            full_key = f"{prefix.value}:{key}" if key else prefix.value
            result = self.redis_client.get(full_key)
            return result.decode('utf-8') if result else None
        except RedisError as e:
            logger.error(f"Failed to retrieve cache for prefix '{prefix}', key '{key}': {e}")
            return None


