from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from .issues.issues_api import router as issues_router
from .report.report_api import router as report_router
from .users.users_api import router as users_router

from .permissions.permissions_api import router as permissions_router
from .auth.auth_api import router as auth_router


http_bearer = HTTPBearer(auto_error=False)

api_v1_preifx = "/api/v1"
router = APIRouter(prefix=api_v1_preifx, dependencies=[Depends(http_bearer)])
router.include_router(router=report_router, prefix='/reports')
router.include_router(router=issues_router, prefix='/issues')
router.include_router(router=users_router, prefix='/users')
router.include_router(router=permissions_router, prefix='/permissions')
router.include_router(router=auth_router, prefix='/auth')