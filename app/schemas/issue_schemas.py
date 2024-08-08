import re
from datetime import datetime
from typing import Literal

from pydantic import Field, validator

from app.schemas.general import BaseUserModel, GeneralSchema


class IssuePostSchema(GeneralSchema):
    description: str | None = Field(None)
    finish_date_plane: datetime | None = Field(validation_alias="finish_date_plane")
    dead_line: datetime | None = Field(validation_alias="dead_line")
    finished_at: datetime | None = Field(None, validation_alias="finished_at")
    rating: Literal[0, 1, 2, 3, 4, 5, None] = Field(None)
    tel: str | None = Field(None)
    email: str | None = Field(None)
    
    state: str | None = Field(None, exclude=True)
    company_name: str | None = Field(None, validation_alias="company_name", exclude=True)
    work_category_title: str = Field(validation_alias="work_category_title", exclude=True)
    building_title: str = Field(validation_alias="building_title", exclude=True)
    priority_title: str | None = Field(validation_alias="priority_title", exclude=True)
    executor_full_name: str | None = Field(validation_alias="executor_full_name", exclude=True)
    room_title: str | None = Field(None, validation_alias="room_title", exclude=True)

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
    
class IssueReportDataSchema(BaseUserModel):
    start_date: datetime = Field(description="123.45") 
    end_date: str = Field(description="123.45") 