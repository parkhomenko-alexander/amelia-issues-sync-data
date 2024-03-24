from datetime import datetime
from typing import TypedDict
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel


class GeneralSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True, alias_generator=to_camel, extra="ignore")

    created_at: datetime | None = Field(None, validation_alias="created_at")
    updated_at: datetime | None = Field(None, validation_alias="updated_at")
    external_id: int = Field(alias="id") #ОСОБЕННОСТИ СУЩНОСТЕЙ КОТОРЫЕ Я СОЗДАЮ САМ

