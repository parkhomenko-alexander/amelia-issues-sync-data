from pydantic import Field
from app.schemas.general import GeneralSchema


class UserPostSchema(GeneralSchema):

    first_name: str | None = Field(None, validation_alias="fname")
    middle_name: str | None = Field(None, validation_alias="mname")
    last_name: str | None = Field(None, validation_alias="lname")
    email: str
    notification_email: str | None = Field(None, validation_alias="notification_email")
    tel: str | None = Field(None)
    role: str = Field(validation_alias="role")
    working: bool = Field(False) 
    facility_id: int | None = Field(None, validation_alias="facility_id")
    company_id: int | None = Field(None, validation_alias="company_id")

    company_name: str  = Field(validation_alias="company_name", exclude=True)
    facilities: str = Field(exclude=True)
