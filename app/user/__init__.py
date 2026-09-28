from aiogram import Router

from .start import router as start_router

user_router = Router()
user_router.include_router(start_router)

__all__ = ["user_router"]
