from enum import Enum

from loguru import logger
from redis import RedisError, StrictRedis

from config import config


class CachePrefixes(Enum):
    BUILDINGS_EXTERNAL_ID_TITLE = "BUILDINGS_EXTERNAL_ID_TITLE"
    BUILDINGS_TITLE_EXTERNAL_ID = "BUILDINGS_TITLE_EXTERNAL_ID"

    ROOMS_EXTERNAL_ID_TITLE = "ROOMS_EXTERNAL_ID_TITLE"
    ROOMS_TITLE_EXTERNAL_ID = "ROOMS_TITLE_EXTERNAL_ID"

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

    async def set_cache(self, prefix: CachePrefixes, mapping: dict[str, int] | dict[int, str]):
        try:
            logger.info(f"Cache was updated for prefix: {prefix}")
            with self.redis_client.pipeline() as pipe:
                for key, value in mapping.items():
                    pipe.hset(f"{prefix.value}", str(key), str(value))
                pipe.execute()
        except RedisError as e:
            logger.error("Failed update cache for preifx '{prefix}': {e}")

