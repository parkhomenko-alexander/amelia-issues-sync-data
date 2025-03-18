from functools import wraps
from time import time
from typing import Any, Callable, Coroutine

from loguru import logger


def perfomance_timer(func: Callable) -> Callable[..., Coroutine[Any, Any, Any]]:
    @wraps(func)
    async def wrapper(*args, **kwargs) -> Coroutine[Any, Any, Any]:
        start_time = time()
        result = await func(*args, **kwargs)
        end_time = time()
        logger.warning(f"{func.__name__} executed in {end_time - start_time:.4f} seconds")
        return result
    return wrapper