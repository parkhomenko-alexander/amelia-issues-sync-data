from app.schemas.general import GeneralSchema


class FacilityPostSchema(GeneralSchema):
    title: str

class Facilities(FacilityPostSchema):
    id: int

