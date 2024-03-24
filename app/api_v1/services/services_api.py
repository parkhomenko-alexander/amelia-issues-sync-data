from fastapi import APIRouter, Request, status
from app.api_v1.dependencies import UowDep
from app.schemas.facility_schemas import FacilityPostSchema

# from app.schemas.services import Service, ServiceBase, ServiceCreate
# from app.services.services import ServicesService 


router = APIRouter(
    tags=['Services']
)


@router.get('/', 
             response_model=FacilityPostSchema,
             status_code=status.HTTP_201_CREATED
             )
async def create_service(
    # service_in: ServiceCreate,
    uow: UowDep,
    request: Request   
):  
    async with uow:
        raise ValueError
    # task_id = await ServicesService(uow).add(service_in)
        return {"message": "Hello World", "root_path": request.scope.get("root_path")}