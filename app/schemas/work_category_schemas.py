from pydantic import Field
from app.schemas.general import GeneralAmeliaSchema


class WorkCategoryPostSchema(GeneralAmeliaSchema):
    title: str
    facility_id: int | None = Field(None, validation_alias="facility_id")
    facility_title: str = Field(validation_alias="facility_title", exclude=True)
    service_title: str = Field(validation_alias="service_title", exclude=True)
    service_id: int | None = Field(None, validation_alias="service_id")