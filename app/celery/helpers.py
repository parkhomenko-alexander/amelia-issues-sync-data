import asyncio
import json
from ast import Tuple
from functools import wraps
from typing import Any, Generic, Type, TypeVar

from pydantic import BaseModel
from requests import Response

from app.schemas.tech_passport_schemas import TechPassportPostSchema


def async_to_sync(task_func):
    @wraps(task_func)
    def wrapper(*args, **kwargs):
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = None

        if loop is None or not loop.is_running():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(task_func(*args, **kwargs))
        else:
            return asyncio.run(task_func(*args, **kwargs))

    return wrapper




T = TypeVar('T', bound=BaseModel)

class ReturnTypeFromJsonQuery(BaseModel, Generic[T]):
    data: list[T]
    count: int

class ReturnTypePathParams(BaseModel, Generic[T]):
    data: list[T]

class DynamicIssuesCount(BaseModel):
    total: int
    filtered: int

class ShortIssue(BaseModel, Generic[T]):
    id: int
    state: str

class DynamicIssuesResponse(BaseModel, Generic[T]):
    data: list[T]
    count: DynamicIssuesCount

    def page_count(self, per_page) -> int:
        if self.count.total == 0:
            return 0
        return self.count.filtered // per_page + 1


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

    object_view: str | None = json.loads(fields[7]["value"])["name"] if fields[7]["value"] else None
    object_class: str | None = json.loads(fields[8]["value"])["name"] if fields[8]["value"] else None
    object_type: str | None = json.loads(fields[9]["value"])["name"] if fields[9]["value"] else None
    organization_3lvl: str | None = json.loads(fields[17]["value"])["name"] if fields[17]["value"] else None
    
    tech_passport = TechPassportPostSchema(
        external_id=room_id,
        title = fields[0]["value"],
        object_view = object_view,
        object_class = object_class,
        object_type = object_type,
        organization_3lvl = organization_3lvl,
        square = fields[21]["value"],
        number_study_places = fields[28]["value"] if fields[28]["value"] else None,

        company_id = fields[1]["value"] if fields[1]["value"] else None,
        organization_2lvl = org_2lvl if org_2lvl != 0 else 29,
        floor_id = fields[2]["value"],
    )

    return tech_passport
