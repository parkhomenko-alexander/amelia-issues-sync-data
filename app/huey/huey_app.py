from huey import RedisHuey

from config import config

huey = RedisHuey(
    'huey_app',
    host=config.REDIS_HOST,
    port=config.REDIS_PORT,
)