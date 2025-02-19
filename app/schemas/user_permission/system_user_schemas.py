from pydantic import Field
from app.schemas.general import GeneralSchema


class SystemUserPostSchema(GeneralSchema):
    login: str = Field(examples=["zxc.zxc@dvfu.ru"])
    email: str = Field(examples=["zxc.zxc@dvfu.ru"])
    password: str = Field(examples=["zxc"])
    timezone: str = Field(examples=["Australia/Brisbane"])

    role_id: int = Field(examples=["1"])


class SystemUserGetSchema(GeneralSchema):
    id: int
    login: str