import asyncio
from functools import wraps
from typing import Any, Generic, Type, TypedDict, TypeVar
from pydantic import BaseModel

from requests import Response


def async_to_sync(task_func):
    @wraps(task_func)
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        return loop.run_until_complete(task_func(*args, **kwargs))
    return wrapper




T = TypeVar('T', bound=BaseModel)

class ReturnTypeFromJsonQuery(BaseModel, Generic[T]):
    data: list[T]
    count: int

class ReturnTypePathParams(BaseModel, Generic[T]):
    data: list[T]


def handle_response_of_json_query(response: Response, model: Type[T]) -> ReturnTypeFromJsonQuery[T]:
    """
        Handling request status and return data
    """
    return ReturnTypeFromJsonQuery[model](**response.json())


def handle_response_of_path_params(response: Response, model: Type[T]) -> ReturnTypePathParams[T]:
    """
        Handling request status and return data
    """

    return ReturnTypePathParams[model](data=response.json())

