from aiogram import Router

from .admin_menu import router as admin_menu_router
from .admins_control import router as admins_control_router
from .newspaper import router as newspaper_router
from .stats import router as stats_router
from .settings_control import router as settings_control_router

admin_router = Router()
admin_router.include_router(admin_menu_router)
admin_router.include_router(admins_control_router)
admin_router.include_router(newspaper_router)
admin_router.include_router(stats_router)
admin_router.include_router(settings_control_router)

__all__ = ["admin_router"]
