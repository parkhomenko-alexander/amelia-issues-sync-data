from app.schemas.general import GeneralAmeliaSchema


class FacilityPostSchema(GeneralAmeliaSchema):
    title: str

class Facilities(FacilityPostSchema):
    id: int

