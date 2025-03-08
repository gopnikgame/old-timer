from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram import html
import httpx
import logging
from datetime import datetime

from app.config import Config
from app.db.predictions import PredictionManager
from app.utils.formatting import format_user

logger = logging.getLogger(__name__)
router = Router()
prediction_manager = PredictionManager()

# Глобальный счётчик запросов к DeepSeek
DEEPSEEK_REQUESTS_COUNT = 0

def build_welcome_message(name: str) -> str:
    return (
        f"<b>🚀 Добро пожаловать, {name}!</b>\n\n"
        "Я твой помощник в этом чате. Вот что я умею:\n"
        "• Отвечать на вопросы\n• Показывать карму\n• Давать предсказания\n\n"
        "Напиши /help чтобы увидеть все команды!"
    )

@router.message(F.chat.id == Config.GROUP_ID, F.content_type == "new_chat_members")
async def handle_new_members(message: Message):
    for user in message.new_chat_members:
        try:
            safe_name = html.escape(user.full_name)
            await message.reply(
                text=build_welcome_message(safe_name),
                parse_mode="HTML",
                reply_markup=ReplyKeyboardRemove(),
                disable_web_page_preview=True
            )
            logger.info(f"Sent welcome to {user.id}")
        except Exception as e:
            logger.error(f"Welcome error: {e}")

def build_help_message() -> str:
    return (
        "<b>🤖 Список доступных команд:</b>\n\n"
        "/help - Показать это сообщение\n"
        "/future - Получить персональное предсказание 🔮\n"
        "/karma - Показать вашу карму 🏆\n"
        "/topkarma - Топ пользователей по карме 🏅\n"
        "/antikarma - Топ антикармы 😈\n"
        "/add_prediction [текст] - Добавить новое предсказание (только для админов)\n\n"
        "<i>Для работы некоторых команд нужно находиться в определённом топике. "
        f"Проверьте {Config.ALLOWED_TOPIC_URL}</i>"
    )

@router.message(F.chat.id == Config.GROUP_ID, Command("help"))
async def send_help(message: Message):
    try:
        await message.reply(
            text=build_help_message(),
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    except Exception as e:
        logger.error(f"Help error: {e}")

async def generate_with_deepseek(prompt: str) -> str:
    global DEEPSEEK_REQUESTS_COUNT
    
    if DEEPSEEK_REQUESTS_COUNT >= Config.DEEPSEEK_DAILY_LIMIT:
        raise ValueError("Достигнут дневной лимит запросов")
    
    headers = {
        "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{
            "role": "user",
            "content": f"Придумай креативное предсказание для чата на тему: {prompt}. "
                      "Используй эмодзи и сделай текст живым. Не используй markdown."
        }],
        "temperature": 0.7,
        "max_tokens": 100
    }
    
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://api.deepseek.com/v1/chat/completions",
            json=payload,
            headers=headers
        )
        
    if response.status_code != 200:
        raise ConnectionError("Ошибка подключения к API")
    
    DEEPSEEK_REQUESTS_COUNT += 1
    return response.json()["choices"][0]["message"]["content"]

@router.message(F.chat.id == Config.GROUP_ID, Command("add_prediction"))
async def add_prediction(message: Message):
    if message.from_user.id not in Config.ALLOWED_IDS:
        return await message.reply("❌ Недостаточно прав!")
    
    try:
        prompt = message.text.split(maxsplit=1)[1]
    except IndexError:
        return await message.reply("ℹ️ Укажите текст для генерации предсказания")
    
    try:
        if DEEPSEEK_REQUESTS_COUNT >= Config.DEEPSEEK_DAILY_LIMIT:
            raise ValueError(
                f"⚠️ Достигнут дневной лимит ({Config.DEEPSEEK_DAILY_LIMIT} запросов). "
                "Попробуйте завтра."
            )
            
        prediction = await generate_with_deepseek(prompt)
        prediction_manager.add_prediction(prediction)
        
        await message.reply(
            f"✅ Новое предсказание добавлено:\n\n{prediction}\n\n"
            f"Использовано запросов сегодня: {DEEPSEEK_REQUESTS_COUNT}/{Config.DEEPSEEK_DAILY_LIMIT}",
            parse_mode="HTML"
        )
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        await message.reply(f"❌ Ошибка: {str(e)}")