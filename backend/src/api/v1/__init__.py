from fastapi import APIRouter
from .docker import router as docker_router
from .chrome import router as chrome_router
from .speedtest import router as speedtest_router

router = APIRouter(prefix="/v1")

router.include_router(docker_router)
router.include_router(chrome_router)
router.include_router(speedtest_router)

__all__ = [
    "router"
]
