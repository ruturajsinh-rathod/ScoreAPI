from fastapi import APIRouter

from src.api.v1.music.controllers import music_router

router = APIRouter(prefix="/api/v1")

# Attach child routers to main router
router.include_router(music_router)

__all__ = ["router"]
