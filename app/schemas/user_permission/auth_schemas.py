from pydantic import ConfigDict
from app.schemas.general import GeneralSchema
from pydantic.alias_generators import to_snake

TOKEN_TYPE = "Bearer"


class TokenSchema(GeneralSchema):
    access_token: str
    refresh_token: str | None = None
    token_type: str = TOKEN_TYPE

    model_config = ConfigDict(
        alias_generator=to_snake
    )

class ShortUserWithRoleSchema(GeneralSchema):
    login: str
    role_id: int

class TokenData(GeneralSchema):
    login:str