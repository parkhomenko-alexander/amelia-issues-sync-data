from pydantic import Field
from app.schemas.general import GeneralSchema


class RoomPostSchema(GeneralSchema):
    title: str

    facility_title: str = Field(validation_alias="facility_title", exclude=True)
    building_title: str = Field(validation_alias="building_title", exclude=True)
    floor_title: str = Field(validation_alias="floor_title", exclude=True)
    company_name: str | None = Field(validation_alias="company_name", exclude=True)

    facility_id: int | None = Field(None, validation_alias="facility_id")
    building_id: int = Field(validation_alias="building_id")
    floor_id: int = Field(validation_alias="floor_id")
    company_id: int | None = Field(None, validation_alias="company_id")
