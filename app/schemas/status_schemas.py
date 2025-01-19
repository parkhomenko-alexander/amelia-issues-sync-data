from datetime import datetime
from pydantic import Field
from app.schemas.general import GeneralSchema


class StatusPostSchema(GeneralSchema):
    title: str
    workflow_id: int = Field(validation_alias="workflow_id")
    is_started: bool = Field(False, validation_alias="started")
    is_terminated: bool = Field(False, validation_alias="terminated")
    is_accepted: bool = Field(False, validation_alias="accepted")
    percentage_completion: int = Field(validation_alias="percentage_completion")

class HistoryStatusRecord(GeneralSchema):
    message: str
    status: str
    percentage: int 
    user: str 
    issue_id: int | None = Field(None)

    updated_at: datetime | None = Field(None, validation_alias="updated_at", exclude=True)
