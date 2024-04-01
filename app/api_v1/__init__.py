from fastapi import APIRouter

from .report.report_api import router as report_router 

router = APIRouter()
router.include_router(router=report_router, prefix='/reports')