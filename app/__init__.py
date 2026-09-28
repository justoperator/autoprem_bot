from aiogram import Router

from .database import UsersControl, AdminsControl
from .settings import Settings
from .admin import admin_router
from .user import user_router

router = Router()
router.include_router(admin_router)
router.include_router(user_router)

__all__ = [
    "UsersControl",
    "AdminsControl",
    "Settings",
    "admin_router",
    "user_router",
    "router",
]
