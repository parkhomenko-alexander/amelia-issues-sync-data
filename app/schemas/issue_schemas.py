import hashlib
import json
import re
from datetime import datetime, timedelta
from typing import Literal
from zoneinfo import ZoneInfo

from pydantic import Field, field_validator, validator

from app.schemas.general import BaseUserModel, GeneralAmeliaSchema
from app.utils.redis_manager import CachePrefixes

AU_TZ = ZoneInfo("Australia/Sydney")

class IssuePostSchema(GeneralAmeliaSchema):
    description: str | None = Field(None)
    finish_date_plane: datetime | None = Field(validation_alias="finish_date_plane")
    dead_line: datetime | None = Field(validation_alias="dead_line")
    finished_at: datetime | None = Field(None, validation_alias="finished_at")
    rating: Literal[0, 1, 2, 3, 4, 5, None] = Field(None)
    tel: str | None = Field(None)
    email: str | None = Field(None)
    work_place: str | None = Field(None, validation_alias="work_place")
    urgency: str | None = Field(None, validation_alias="urgency")
    
    state: str | None = Field(None, exclude=True)
    company_name: str | None = Field(None, validation_alias="company_name", exclude=True)
    work_category_title: str = Field(validation_alias="work_category_title", exclude=True)
    building_title: str = Field(validation_alias="building_title", exclude=True)
    priority_title: str | None = Field(validation_alias="priority_title", exclude=True)
    executor_full_name: str | None = Field(validation_alias="executor_full_name", exclude=True)
    room_title: str | None = Field(None, validation_alias="room_title", exclude=True)

    facility_id: int | None = Field(2, validation_alias="facility_id")
    company_id: int | None = Field(None, validation_alias="company_id")
    service_id: int = Field(validation_alias="service_id")
    work_category_id: int | None = Field(None, validation_alias="work_category_id")
    workflow_id: int = Field(validation_alias="workflow_id") 
    declarer_id: int | None = Field(validation_alias="user_id") 
    building_id: int | None = Field(None, validation_alias="building_id")
    priority_id: int | None = Field(None, validation_alias="priority_id")
    executor_id: int | None = Field(None, validation_alias="executor_id")
    room_id: int | None = Field(None, validation_alias="room_id")

    @validator("description")
    def clean_html(cls, raw_html: str):
        CLEANRE = re.compile("<.*?>")
        cleantext = re.sub(CLEANRE, "", raw_html)
        return cleantext

class IssueReportSchema(BaseUserModel):
    ...


def start_date() -> datetime:
    return datetime(2020, 7, 1, 0, 0, 0)

def end_date() -> datetime:
    return datetime.now() + timedelta(days=10)

def start_time_example() -> datetime:
    return datetime.fromisoformat("2024-08-05T00:00:00")

def end_time_example() -> datetime:
    return datetime.fromisoformat("2024-09-05T00:00:00")

class IssueReportDataSchema(BaseUserModel):
    start_date: datetime = Field(description="123.45") 
    end_date: str = Field(description="123.45") 

class CreationTime(BaseUserModel):
    start_date: datetime = Field(
        default_factory=start_date,
        examples=["2024-08-05T00:00:00"],
        description="Start date and time in ISO format."
    )
    end_date: datetime = Field(
        default_factory=end_date,
        examples=["2024-09-05T00:00:00"],
        description="End date and time in ISO format."
    )

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def prepare_datetime(cls, value, field):
        if value is None:
            value = start_date() if field.field_name == "start_date" else end_date()

        if isinstance(value, str):
            value = datetime.fromisoformat(value)

        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=AU_TZ)
            value = value.astimezone(ZoneInfo("UTC"))

        return value



class TransitionStatuses(BaseUserModel):
    start_date: datetime = Field(
        default_factory=start_date,
        examples=["2024-09-10T00:00:00"],
        description="End date and time in ISO format."
    )
    end_date: datetime = Field(
        default_factory=end_date,
        examples=["2024-09-30T00:00:00"],
        description="End date and time in ISO format."
    )
    statuses: list[str] | None = Field(
        default=None,
        examples=[["взята в работу"]],
        description="Buildings"
    )

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def prepare_datetime(cls, value, field):
        if value is None:
            value = start_date() if field.field_name == "start_date" else end_date()

        if isinstance(value, str):
            value = datetime.fromisoformat(value)

        if isinstance(value, datetime):
            if value.tzinfo is None:
                value = value.replace(tzinfo=AU_TZ)
            value = value.astimezone(ZoneInfo("UTC"))

        return value


class Place(BaseUserModel):
    buildings_id: list[int] | None = Field(
        default_factory=None,
        examples=[[45,46]],
        description="Buildings"
    )
    rooms_id: list[int] | None = Field(
        default_factory=list,
        examples=[[18000, 18001]],
        description="Rooms"
    )

    @field_validator("buildings_id", "rooms_id", mode="before")
    @classmethod
    def empty_list_to_none(cls, value):
        if isinstance(value, list) and len(value) == 0:
            return None
        return value

class Work(BaseUserModel):
    services_id: list[int] | None = Field(
        default_factory=list,
        examples=[[7, 10]],
        description="Services"
    )

    work_categories_id: list[int] | None = Field(
        default_factory=list,
        examples=[[200, 399]],
        description="Work categories"
    )

    @field_validator("services_id", "work_categories_id", mode="before")
    @classmethod
    def empty_list_to_none(cls, value):
        if isinstance(value, list) and len(value) == 0:
            return None
        return value

class Pagination(BaseUserModel):
    limit: int = Field(50, ge=10, le=10000)
    offset: int = Field(0, ge=0)


def transition_statuses_factory() -> TransitionStatuses:
    return TransitionStatuses(
        start_date=start_date(),
        end_date=end_date(),
        statuses=[]
    )

def creation_factory() -> CreationTime:
    return CreationTime(
        start_date=start_date(),
        end_date=end_date(),
    )

def place_factory() -> Place:
    return Place(
        buildings_id=[],
        rooms_id=[]
    )

def work_factory() -> Work:
    return Work(
        services_id=[],
        work_categories_id=[]
    )
def pagination_factory() -> Pagination:
    return Pagination(
        limit=50,
        offset=1
    ) 

class IssuesFiltersSchema(BaseUserModel):
    transition: TransitionStatuses = Field(
        default_factory=transition_statuses_factory,
        description="Filters for transition statuses."
    )
    place: Place = Field(
        default_factory=place_factory,
        description="Place of work"
    )
    creation: CreationTime = Field(
        default_factory=creation_factory,
    )
    work: Work = Field(
        default_factory=work_factory,
        description="Work res"
    )
    urgency: list[str] | None = Field(
        examples=[],
        default=None
    )
    priorities_id: list[int] | None = Field(
        default=None
    )
    pagination: Pagination = Field(
        default_factory=pagination_factory
    )
    current_statuses: list | None = Field(
        default=None,
        examples=[["новая", "принята"]],
    )

    @field_validator("urgency", "priorities_id", "current_statuses", mode="before")
    @classmethod
    def empty_list_to_none(cls, value):
        if isinstance(value, list) and not value:
            return None
        return value


    @staticmethod
    def build_cache_key(filters: "IssuesFiltersSchema", debug: bool = False) -> str:
        dumped = json.dumps(
            filters.model_dump(exclude={"pagination"}),
            sort_keys=True,
            separators=(",", ":"),
            default=str
        )

        prefix = CachePrefixes.ISSUES.value

        if debug:
            return f"{prefix}:count_filtered_issues_{dumped}"

        hashed = hashlib.sha256(dumped.encode("utf-8")).hexdigest()
        return f"{prefix}:count_filtered_issues_{hashed}"

class FilteredIssue(BaseUserModel):
    id: int
    service_title: str
    wc_title: str
    iss_descr: str

    last_status: str

    created_at_first_stat: datetime
    end_date: datetime | None
    close_date: datetime | None
    finish_date_plan: datetime | None

    rating: int | None
    building_title: str | None
    room_title: str | None
    work_place: str | None

    prior_title: str

class FilteredIssuesGetSchema(BaseUserModel):
    filtered_count: int
    total_count: int
    issues: list[FilteredIssue]

class ThinDict(BaseUserModel):
    id: int
    title: str

class WorkCat(ThinDict):
    service_id: int

class IssueFilters(BaseUserModel):
    buildings: list[ThinDict]
    services: list[ThinDict]
    work_categories: list[WorkCat]
    priorities: list[ThinDict]
    statuses: list[str]