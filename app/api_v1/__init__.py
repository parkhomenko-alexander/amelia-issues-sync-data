from fastapi import APIRouter

from .issues.issues_api import router as issues_router
from .report.report_api import router as report_router

router = APIRouter()
router.include_router(router=report_router, prefix='/reports')
router.include_router(router=issues_router, prefix='/issues')