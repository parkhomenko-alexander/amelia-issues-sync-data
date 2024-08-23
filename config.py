import os

from dotenv import find_dotenv, load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import false

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

    DB_URI: str = "" 
    DB_ECHO: bool = False 

    CELERY_BROKER_URL: str = "" 
    CELERY_RESULT_BACKEND: str = "" 
    FAST_API_CACHE: str = "" 

    API_BASE_URL: str = "" 
    API_USER: str = "" 
    API_USER_PASSWORD: str = ""
    API_CALLS_DELAY: float = 3
    API_CALLS_TIMEOUT_DELAY: float = 3

    model_config = SettingsConfigDict(env_file=DOTENV)

config = Config()