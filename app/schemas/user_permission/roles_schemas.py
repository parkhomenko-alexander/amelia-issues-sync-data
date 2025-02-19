from app.schemas.general import GeneralSchema, GeneralAmeliaSchema


class RolePostSchema(GeneralSchema):
    title: str


class RoleGetSchema(GeneralSchema):
    title: str
    id: int 