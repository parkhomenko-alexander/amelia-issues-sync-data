from app.schemas.general import GeneralSchema, GeneralAmeliaSchema


class ShortUserSchema(GeneralSchema):
    login: str
    password: str

class TokenSchema(GeneralSchema):
    access_token: str
    refresh_token: str | None
    token_type: str = "Bearer"

class ShortUserWithRoleSchema(GeneralSchema):
    login: str
    role_id: int