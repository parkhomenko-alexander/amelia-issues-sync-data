from pydantic import Field
from app.schemas.general import GeneralSchema


class ServicePostSchema(GeneralSchema):
    title: str
    facility_id: int | None = Field(None, validation_alias="facility_id")
    facility_title: str = Field(validation_alias="facility_title", exclude=True)