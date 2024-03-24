from pydantic import Field
from app.schemas.general import GeneralSchema


class WorkflowPostSchema(GeneralSchema):
    title: str
    facility_title: str = Field(validation_alias="facility_title", exclude=True)
    facility_id: int | None = Field(None, validation_alias="facility_id")

class WorkflowGetSchema(GeneralSchema):
    id: int 
    title: str
    external_id: int = Field(validation_alias="external_id")
    facility_id: int = Field(validation_alias="facility_id", exclude=True)