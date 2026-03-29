from fastapi import APIRouter

from .chrome import router as chrome_router
from .docker import router as docker_router
from .logs import router as logs_router
from .settings import router as settings_router
from .speedtest import router as speedtest_router

router = APIRouter(prefix="/v1", tags=["v1"])

router.include_router(docker_router)
router.include_router(chrome_router)
router.include_router(speedtest_router)
router.include_router(settings_router)
router.include_router(logs_router)

__all__ = ["router"]
