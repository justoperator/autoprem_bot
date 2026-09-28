import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

load_dotenv()

# Get bot token from environment variable or configure it here
TOKEN = os.getenv("BOT_TOKEN", "")

# Initialize bot if token is provided
bot = (
    Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    if TOKEN
    else None
)
dp = Dispatcher(storage=MemoryStorage())
