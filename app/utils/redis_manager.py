from enum import Enum

from loguru import logger
from redis import RedisError, StrictRedis

from config import config


class CachePrefixes(Enum):
    BUILDINGS_ROOMS_INFO = "BUILDINGS_INFO"


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

    async def set_cache(self, prefix: CachePrefixes, val: str):
        try:
            logger.info(f"Cache was updated for prefix: {prefix}")
            with self.redis_client.pipeline() as pipe:
                pipe.set(f"{prefix.value}", val)
                pipe.execute()
        except RedisError as e:
            logger.error("Failed update cache for preifx '{prefix}': {e}")

