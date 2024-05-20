import asyncio
from functools import wraps
from typing import Any, Generic, Type, TypeVar
from pydantic import BaseModel

from requests import Response

from app.schemas.tech_passport_schemas import TechPassportPostSchema


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

def handle_response_of_tech_passports(response: Response, model: Type[TechPassportPostSchema], room_id: int) -> TechPassportPostSchema:
    """
        Handling request status and return data
    """
    response_json = response.json()
    fields = response_json["fields"]
    org_2lvl = fields[16]["value"]
    tech_passport = TechPassportPostSchema(
        external_id=room_id,
        title = fields[0]["value"],
        object_view = fields[7]["value"],
        object_class = fields[8]["value"],
        object_type = fields[9]["value"],
        organization_3lvl = fields[17]["value"],
        square = fields[21]["value"],
        number_study_places = fields[28]["value"],

        company_id = fields[1]["value"],
        organization_2lvl = org_2lvl if org_2lvl != 0 else 29,
        floor_id = fields[2]["value"],
    )

    return tech_passport