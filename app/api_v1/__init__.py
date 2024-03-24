from fastapi import APIRouter

from .services.services_api import router as services_router 
# from .work_categories.views import router as work_categories_router

router = APIRouter()
router.include_router(router=services_router, prefix='/services')
# router.include_router(router=work_categories_router, prefix='/work_categories')