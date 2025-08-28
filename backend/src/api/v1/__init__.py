from fastapi import APIRouter
from .docker import router as docker_router
router = APIRouter(prefix="/v1")

router.include_router(docker_router)

__all__ = [
    "router"
]
