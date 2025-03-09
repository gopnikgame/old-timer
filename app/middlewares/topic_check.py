import logging
from typing import Callable, Awaitable, Any

from aiogram import BaseMiddleware
from aiogram.types import Message
from app.config import Config

logger = logging.getLogger(__name__)

class TopicCheckMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: dict[str, Any]
    ) -> Any:
        if event.chat.id == Config.GROUP_ID and event.message_thread_id != Config.ALLOWED_TOPIC_ID:
            logger.warning(f"Сообщение от пользователя {event.from_user.id} в неразрешенном топике.")
            return  # Игнорируем сообщение

        return await handler(event, data)