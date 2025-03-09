import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import Config
from app.handlers import base, karma  # Импортируем handlers
from app.middlewares.logging import LoggingMiddleware
from app.middlewares.topic_check import TopicCheckMiddleware  # Импортируем middleware
from app.db.database import init_db, db  # Import database

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def main():
    # Объект бота
    bot = Bot(token=Config.BOT_TOKEN, parse_mode=ParseMode.HTML)

    # Диспетчер
    dp = Dispatcher(storage=MemoryStorage())

    # Регистрация middlewares
    dp.message.middleware(LoggingMiddleware())
    dp.message.middleware(TopicCheckMiddleware())  # Регистрируем middleware для проверки топика

    # Регистрация handlers
    dp.include_router(base.router)
    dp.include_router(karma.router)  # Подключаем handlers для кармы

    # Initialize database
    await init_db()

    # Запуск polling
    try:
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()
        await db.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")