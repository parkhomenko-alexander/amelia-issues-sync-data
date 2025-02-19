from pydantic import Field
from app.schemas.general import GeneralAmeliaSchema


class ServicePostSchema(GeneralAmeliaSchema):
    title: str
    facility_id: int | None = Field(None, validation_alias="facility_id")
    facility_title: str = Field(validation_alias="facility_title", exclude=True)