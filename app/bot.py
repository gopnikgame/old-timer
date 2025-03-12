import asyncio
import logging
import os
from logging.handlers import RotatingFileHandler

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage

from app.config import Config
from app.handlers import base, karma  # Импортируем handlers
from app.middlewares.logging import LoggingMiddleware
from app.middlewares.topic_check import TopicCheckMiddleware  # Импортируем middleware
from app.db.database import init_db, db  # Import database
from app.utils.formatting import format_user

# Создаем директорию для логов, если она не существует
LOG_DIR = "/opt/old-timer/logs"
os.makedirs(LOG_DIR, exist_ok=True)

# Настройка логирования
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)

# Настройка логирования в файл
logger = logging.getLogger(__name__)

# Обработчик для всех логов
file_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "bot.log"),
    maxBytes=10*1024*1024,  # 10 МБ
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
logger.addHandler(file_handler)

# Обработчик только для ошибок
error_handler = RotatingFileHandler(
    os.path.join(LOG_DIR, "error.log"),
    maxBytes=5*1024*1024,  # 5 МБ
    backupCount=3,
    encoding='utf-8'
)
error_handler.setFormatter(logging.Formatter(LOG_FORMAT))
error_handler.setLevel(logging.ERROR)
logger.addHandler(error_handler)

# Добавляем обработчики к корневому логгеру для перехвата всех логов
root_logger = logging.getLogger()
root_logger.addHandler(file_handler)
root_logger.addHandler(error_handler)

logger.info("Logger initialized")

async def main():
    # Объект бота
    bot = Bot(token=Config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

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
        logger.info("Bot started")
        await dp.start_polling(bot, skip_updates=True)
    finally:
        await bot.session.close()
        await db.close()
        logger.info("Bot stopped")

if __name__ == "__main__":
    try:
        print("Запуск бота...")
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
    except Exception as e:
        logger.exception(f"Critical error: {e}")
        print(f"Критическая ошибка: {e}")