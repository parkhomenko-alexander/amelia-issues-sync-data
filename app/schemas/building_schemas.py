from ast import Dict

from pydantic import BaseModel, Field

from app.schemas.general import GeneralSchema


class BuildingPostSchema(GeneralSchema):
    title: str
    facility_id: int | None = Field(None, validation_alias="facility_id")
    facility_title: str = Field(validation_alias="facility_title", exclude=True)
    address: str | None = Field(None)
    latitude: float | None = Field(None)
    longitude: float | None = Field(None)


RoomForCahce = dict[str, int]

class BuildingForCache(BaseModel):
    id: int
    rooms: RoomForCahce

BuildingsForCache = dict[str, BuildingForCache]