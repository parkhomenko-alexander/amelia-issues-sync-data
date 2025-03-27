from functools import wraps
from time import time
from typing import Any, Awaitable, Callable, Coroutine, ParamSpec, TypeVar

from loguru import logger

P = ParamSpec("P")
R = TypeVar("R")

def perfomance_timer(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
    @wraps(func)
    async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start_time = time()
        result = await func(*args, **kwargs)
        end_time = time()
        logger.warning(f"{func.__name__} executed in {end_time - start_time:.4f} seconds")
        return result
    return wrapper