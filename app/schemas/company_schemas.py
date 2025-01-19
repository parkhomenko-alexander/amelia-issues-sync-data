from pydantic import Field
from app.schemas.general import GeneralSchema


class CompanyPostSchema(GeneralSchema):
    facility_id: int | None = Field(None, validation_alias="facility_id")
    full_name: str = Field(validation_alias="full_name")
    facility_title: str = Field(validation_alias="facility_title", exclude=True)

class CompanyOrmSсheme(GeneralSchema):
    full_name: str = Field(validation_alias="full_name")
    facility_id: int = Field(validation_alias="facility_id")

class CompanyGetSchema(CompanyPostSchema):
    id: int
