import os
from loguru import logger
from config import config

log_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    config.APPLICATION_LOGGER_PATH, 
    f"{config.APPLICATION_LOGGER_FILENAME}"
)

logger.add(
    log_path,
    format=f"{config.APPLICATION_LOGGER_FORMAT}",
    # level=f"{config.APPLICATION_LOGGER_LEVEL}",
    rotation=f"{config.APPLICATION_LOGGER_ROTATION}",
    compression=f"{config.APPLICATION_LOGGER_COMPRESSION}",
    serialize=config.APPLICATION_LOGGER_SERIALIZE
)