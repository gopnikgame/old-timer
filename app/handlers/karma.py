from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
import logging

from app.config import Config
from app.db.karma import get_karma, update_karma, get_top_karma, get_bottom_karma
from app.utils.formatting import format_user

logger = logging.getLogger(__name__)
router = Router()

@router.message(F.chat.id == Config.GROUP_ID, Command("karma"))
async def show_karma(message: Message):
    try:
        user_id = message.from_user.id
        karma_value = await get_karma(user_id)
        
        await message.reply(
            f"🏆 {format_user(message.from_user)}, ваша карма: {karma_value}",
            parse_mode="HTML"
        )
        logger.info(f"Karma shown for user {user_id}")
    except Exception as e:
        logger.exception(f"Error showing karma: {e}")
        await message.reply("❌ Произошла ошибка при получении кармы")

@router.message(F.chat.id == Config.GROUP_ID, Command("topkarma"))
async def show_top_karma(message: Message):
    try:
        top_users = await get_top_karma(10)  # Получаем топ-10
        
        if not top_users:
            return await message.reply("📊 Информация о карме пока недоступна")
        
        response = "🏅 <b>Топ пользователей по карме:</b>\n\n"
        
        # В этом месте нам нужно получить информацию о пользователях
        # Но для упрощения выведем только ID и значение кармы
        for i, record in enumerate(top_users, 1):
            response += f"{i}. ID: {record['user_id']} — {record['karma']} очков\n"
        
        await message.reply(response, parse_mode="HTML")
        logger.info("Top karma shown")
    except Exception as e:
        logger.exception(f"Error showing top karma: {e}")
        await message.reply("❌ Произошла ошибка при получении топа кармы")

@router.message(F.chat.id == Config.GROUP_ID, Command("antikarma"))
async def show_bottom_karma(message: Message):
    try:
        bottom_users = await get_bottom_karma(10)  # Получаем анти-топ-10
        
        if not bottom_users:
            return await message.reply("📊 Информация о карме пока недоступна")
        
        response = "😈 <b>Антирейтинг кармы:</b>\n\n"
        
        # В этом месте нам нужно получить информацию о пользователях
        # Но для упрощения выведем только ID и значение кармы
        for i, record in enumerate(bottom_users, 1):
            response += f"{i}. ID: {record['user_id']} — {record['karma']} очков\n"
        
        await message.reply(response, parse_mode="HTML")
        logger.info("Bottom karma shown")
    except Exception as e:
        logger.exception(f"Error showing bottom karma: {e}")
        await message.reply("❌ Произошла ошибка при получении антитопа кармы")

# Обработчик для изменения кармы через реакции на сообщения
@router.message(F.chat.id == Config.GROUP_ID, F.text.regexp(r"^(\+|\-)$"))
async def karma_reaction(message: Message):
    # Проверяем, что сообщение является ответом на другое
    if not message.reply_to_message:
        return
    
    target_user = message.reply_to_message.from_user
    current_user = message.from_user
    
    # Пользователь не может изменять свою карму
    if target_user.id == current_user.id:
        return await message.reply("❌ Вы не можете изменять свою карму")
    
    # Определяем изменение кармы
    karma_change = 1 if message.text == "+" else -1
    
    # Обновляем карму
    success = await update_karma(target_user.id, karma_change)
    if success:
        new_karma = await get_karma(target_user.id)
        
        # Отправляем сообщение о изменении кармы
        if karma_change > 0:
            await message.reply(
                f"⬆️ {format_user(current_user)} повысил карму пользователя {format_user(target_user)}\n"
                f"Текущая карма: {new_karma}",
                parse_mode="HTML"
            )
        else:
            await message.reply(
                f"⬇️ {format_user(current_user)} понизил карму пользователя {format_user(target_user)}\n"
                f"Текущая карма: {new_karma}",
                parse_mode="HTML"
            )
    
    logger.info(f"Karma {karma_change} by {current_user.id} to {target_user.id}")
