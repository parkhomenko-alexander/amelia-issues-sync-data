from pydantic import Field
from app.schemas.general import GeneralSchema


class FloorPostSchema(GeneralSchema):
    title: str
    facility_id: int | None = Field(None, validation_alias="facility_id")
    facility_title: str = Field(validation_alias="facility_title", exclude=True)
    building_id: int = Field(validation_alias="building_id")
    building_title: str = Field(validation_alias="building_title", exclude=True)