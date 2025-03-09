import logging

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler,
        event: TelegramObject,
        data: dict
    ):
        user = data.get("event_from_user")
        if user:
            logger.info(f"User {user.id} ({user.username}) triggered {event.__class__.__name__}")
        else:
            logger.info(f"Event {event.__class__.__name__} triggered")
        return await handler(event, data)