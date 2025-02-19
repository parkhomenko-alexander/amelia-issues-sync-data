from app.schemas.general import GeneralAmeliaSchema


class PermissionPost(GeneralAmeliaSchema):
    title: str
    description: str


class PermissionGet(GeneralAmeliaSchema):
    id: int