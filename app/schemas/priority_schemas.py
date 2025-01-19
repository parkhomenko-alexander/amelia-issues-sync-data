from pydantic import Field
from app.schemas.general import GeneralSchema


class PriorityPostSchema(GeneralSchema):
    title: str = Field(validation_alias="title")
    weight: int = Field(validation_alias="weight")
    facility_title: str = Field(validation_alias="facility_title", exclude=True)
    facility_id: int | None = Field(None, validation_alias="facility_id")


class PriorityOrmSchema(GeneralSchema):
    ...

class PriorityGetSchema(GeneralSchema):
    ...