from app.routes.admin import admin_router
from app.routes.bot import main_router
from app.routes.gpt_image import gpt_image_router
from app.routes.runway import runway_router
from app.routes.flux import flux_router
from app.routes.mj_image import mj_image_router
from app.routes.mj_video import mj_video_router
from app.routes.nano_banana import nano_banana_router
from app.routes.kling import kling_router
from app.routes.sora import sora_router

__all__ = [
    "main_router",
    "admin_router",
    "runway_router",
    "gpt_image_router",
    "flux_router",
    "mj_image_router",
    "mj_video_router",
    "nano_banana_router",
    "kling_router",
    "sora_router"
]
