from fastapi import APIRouter, Request, status
from fastapi.responses import FileResponse
from app.api_v1.dependencies import UowDep
from app.services.room_service import RoomService


router = APIRouter(
    tags=['Reports']
)


@router.get(
    '/general_rooms_report', 
    # response_model=FacilityPostSchema,
    # status_code=status.HTTP_201_CREATED
)
async def generate_general_report(
    uow: UowDep,
    request: Request,
    response_class=FileResponse  
):  
    try:
        room_service = RoomService(uow)
        file_report = await room_service.generate_general_rooms_report()
        return FileResponse(path=file_report, filename="file.xlsx", media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

    except Exception as error:
        print(error)