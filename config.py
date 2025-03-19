from functools import lru_cache
import os

from pydantic_settings import BaseSettings, SettingsConfigDict

DOTENV = os.path.join(os.path.dirname(__file__), ".env")

class Config(BaseSettings):
    APPLICATION_HOST: str = ""
    APPLICATION_PORT: int = 0
    APPLICATION_LOG_LEVEL: str = ""
    APPLICATION_DEBUG: bool = False
    APPLICATION_PREFIX_BEHIND_PROXY: str = ""
    APPLICATION_API_PREFIX: str = ""
    APPLICATION_LOGGER_PATH: str = ""
    APPLICATION_LOGGER_FILENAME: str = ""
    APPLICATION_LOGGER_FORMAT: str = ""
    # APPLICATION_LOGGER_LEVEL: str = ""
    APPLICATION_LOGGER_ROTATION: str = ""
    APPLICATION_LOGGER_COMPRESSION: str = ""
    APPLICATION_LOGGER_SERIALIZE: bool = False

    APPLICATION_SECRET_KEY: str = ""
    APPLICATION_HASH_ALGORITHM: str = ""
    APPLICATION_ACCESS_TOKEN_EXPIRE_MINUTES: int = 0
    APPLICATION_REFRESH_TOKEN_EXPIRE: int = 0

    APPLICATION_INIT_DB_DATA_PATH: str = ""
    APPLICATION_INIT_DB_DATA_FILENAME: str = ""

    DB_URI: str = ""
    DB_ECHO: bool = False 

    CELERY_BROKER_URL: str = ""
    CELERY_RESULT_BACKEND: str = ""
    REDIS_HOST: str = ""
    REDIS_PORT: int = 0
    REDIS_DB: int = 0 
    FAST_API_CACHE: str = ""

    API_BASE_URL: str = ""
    API_USER: str = ""
    API_USER_PASSWORD: str = ""
    API_USER_ID: str = ""
    API_CALLS_DELAY: float = 3
    API_CALLS_TIMEOUT_DELAY: float = 3


    model_config = SettingsConfigDict(env_file=DOTENV, extra="ignore")

    def get_redis_uri(self) -> str:
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

config = Config()

@lru_cache
def get_config() -> Config:
    return Config()