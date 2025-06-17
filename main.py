import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from helper.bot.handlers.user import user_router
from helper.bot.handlers.admin import admin_router
from log_tools.log_worker import log_queue, log_worker
from config import BOT_TOKEN


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="help", description="Описание"),
    ]
    await bot.set_my_commands(commands)


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    await set_commands(bot)

    dp.include_routers(admin_router, user_router)

    asyncio.create_task(log_worker(log_queue))  #запуск очереди для записи в эксель
    
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
