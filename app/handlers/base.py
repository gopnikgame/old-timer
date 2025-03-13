from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
import html  # Стандартный модуль Python для экранирования HTML
import logging
from datetime import datetime

from app.config import Config
from app.db.predictions import add_prediction as db_add_prediction  # Переименовываем импортированную функцию
from app.db.predictions import get_prediction  # Добавляем импорт для /future
from app.utils.formatting import format_user
from app.utils.gigachat_api import GigaChatAPI  # Импорт нового класса для API

logger = logging.getLogger(__name__)
router = Router()

# Создаем экземпляр класса GigaChatAPI
gigachat_api = GigaChatAPI()

# Глобальный счётчик запросов к GigaChat
GIGACHAT_REQUESTS_COUNT = 0

def build_welcome_message(name: str) -> str:
    return (
        f"<b>🚀 Добро пожаловать, {name}!</b>\n\n"
        "Я твой помощник в этом чате. Вот что я умею:\n"
        "• Отвечать на вопросы\n• Показывать карму\n• Давать предсказания\n\n"
        "Напиши /help чтобы увидеть все команды!"
    )

@router.message(F.chat.type.in_({"private"}), Command("start"))
async def cmd_start(message: Message):
    try:
        user_name = html.escape(message.from_user.full_name)
        await message.reply(
            text=build_welcome_message(user_name),
            disable_web_page_preview=True
        )
        logger.info(f"Sent start message to user {message.from_user.id}")
    except Exception as e:
        logger.exception(f"Start command error: {e}")

@router.message(F.chat.id == Config.GROUP_ID, F.content_type == "new_chat_members")
async def handle_new_members(message: Message):
    for user in message.new_chat_members:
        try:
            safe_name = html.escape(user.full_name)
            await message.reply(
                text=build_welcome_message(safe_name),
                reply_markup=ReplyKeyboardRemove(),
                disable_web_page_preview=True
            )
            logger.info(f"Sent welcome to {user.id}")
        except Exception as e:
            logger.exception(f"Welcome error: {e}")

def build_help_message() -> str:
    # Базовый текст справки
    help_text = (
        "<b>🤖 Список доступных команд:</b>\n\n"
        "/help - Показать это сообщение\n"
        "/future - Получить персональное предсказание 🔮\n"
        "/karma - Показать вашу карму 🏆\n"
        "/topkarma - Топ пользователей по карме 🏅\n"
        "/antikarma - Топ антикармы 😈\n"
        "/add_prediction [текст] - Добавить новое предсказание на указанную тему (только для админов)\n\n"
    )
    
    # Добавляем информацию о топике только если он настроен
    if Config.ALLOWED_TOPIC_ID is not None and Config.ALLOWED_TOPIC_URL != "этот чат":
        help_text += (
            f"<i>Для работы некоторых команд нужно находиться в определённом топике. "
            f"Проверьте {Config.ALLOWED_TOPIC_URL}</i>"
        )
    
    return help_text

@router.message(F.chat.id == Config.GROUP_ID, Command("help"))
async def send_help(message: Message):
    try:
        await message.reply(
            text=build_help_message(),
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.exception(f"Help error: {e}")

@router.message(F.chat.type.in_({"private"}), Command("help"))
async def private_send_help(message: Message):
    try:
        await message.reply(
            text=build_help_message(),
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.exception(f"Private help error: {e}")

# Добавляем обработчик команды /future, которая упоминается в help_message
@router.message(Command("future"))
async def cmd_future(message: Message):
    try:
        user = message.from_user
        prediction = await get_prediction()
        
        await message.reply(
            f"🔮 {format_user(user)}, ваше предсказание:\n\n{prediction}",
            disable_web_page_preview=True
        )
        logger.info(f"Prediction sent to user {user.id}")
    except Exception as e:
        logger.exception(f"Future prediction error: {e}")
        await message.reply("❌ Ошибка при получении предсказания")

@router.message(Command("add_prediction"))
async def add_new_prediction(message: Message):
    if message.from_user.id not in Config.ALLOWED_IDS:
        return await message.reply("❌ Недостаточно прав!")

    # Проверяем, содержится ли промт в сообщении
    try:
        # Пытаемся получить текст после команды
        command_parts = message.text.split(maxsplit=1)
        
        # Если длина массива равна 1, значит промт отсутствует
        if len(command_parts) == 1:
            # Отправляем подробную подсказку
            return await message.reply(
                "ℹ️ Для создания нового предсказания укажите тему:\n\n"
                "/add_prediction [тема предсказания]\n\n"
                "Например:\n"
                "/add_prediction работа и карьера\n"
                "/add_prediction любовь и отношения\n"
                "/add_prediction здоровье и благополучие\n\n"
                "Модель GigaChat создаст креативное предсказание на указанную тему."
            )
        
        # Если промт указан, получаем его
        prompt = command_parts[1]
    except IndexError:
        return await message.reply("ℹ️ Укажите текст для генерации предсказания")

    try:
        global GIGACHAT_REQUESTS_COUNT
        if GIGACHAT_REQUESTS_COUNT >= Config.GIGACHAT_DAILY_LIMIT:
            raise ValueError(
                f"⚠️ Достигнут дневной лимит ({Config.GIGACHAT_DAILY_LIMIT} запросов). "
                "Попробуйте завтра."
            )

        # Используем GigaChatAPI для генерации предсказания
        prediction = await gigachat_api.generate_prediction(prompt)
        # Используем существующую функцию для добавления предсказания в БД
        await db_add_prediction(message.from_user.id, prediction)

        GIGACHAT_REQUESTS_COUNT += 1
        await message.reply(
            f"✅ Новое предсказание добавлено:\n\n{prediction}\n\n"
            f"Использовано запросов сегодня: {GIGACHAT_REQUESTS_COUNT}/{Config.GIGACHAT_DAILY_LIMIT}"
        )

    except Exception as e:
        logger.error(f"Prediction error: {e}")
        await message.reply(f"❌ Ошибка: {str(e)}")