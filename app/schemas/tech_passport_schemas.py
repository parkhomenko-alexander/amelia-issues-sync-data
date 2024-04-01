import uuid
from loguru import logger
from pydantic import BaseModel, Field, validator


class TechPassportPostSchema(BaseModel):
    title: str
    object_view: str | None = Field(None)
    object_type: str | None = Field(None)
    object_class: str | None = Field(None)
    organization_3lvl: str | None = Field(None)
    square: float | None | str = Field(None)
    number_study_places: float | None | str = Field(None)

    company_id: int | None = Field(None)
    organization_2lvl: int | None = Field(None)
    floor_id: int | None = Field(None)

    external_id: int = Field()

    @validator("square", always=True)
    def normalize_square(cls, square: float | None | str, values: dict):
        try:
            if square is None or square == "":
                return None
            return float(square)
        except Exception as err:
            tp_id = values.get("external_id")
            logger.error(f"Eror square: {err} {tp_id}")
            return 0

    
    @validator("number_study_places")
    def normalize_study_places(cls, study_places: float | None | str):
        if study_places is None or study_places == "":
            return None

        return float(study_places)