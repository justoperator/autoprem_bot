import asyncio
import logging
from datetime import datetime

from config import bot, dp, TOKEN
from app import router


async def main():
    """Main entry point for running the aiogram bot."""
    if not TOKEN or not bot:
        print("[ERROR] BOT_TOKEN is not set! Please set BOT_TOKEN in .env or config.py.")
        return

    dp.include_router(router)

    # Drop any pending updates before polling
    try:
        await bot.delete_webhook(drop_pending_updates=True)
    except Exception as e:
        print(f"[WARNING] Could not delete webhook: {e}")

    try:
        bot_info = await bot.get_me()
        print(f"Bot is working! (@{bot_info.username}) ({datetime.now()})")
    except Exception as e:
        print(f"[ERROR] Failed to fetch bot information: {e}")

    while True:
        try:
            await dp.start_polling(bot)
        except Exception as e:
            print(
                f"[ERROR] In bot polling:\n\n"
                f"{e}"
            )
            await asyncio.sleep(5)
            continue


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")
