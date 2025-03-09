import asyncio
import time
import logging
from datetime import datetime, timedelta
from tinydb import TinyDB, Query
from pathlib import Path
from app.config import Config

logger = logging.getLogger(__name__)

class KarmaManager:
    def __init__(self):
        self.db = TinyDB(Config.KARMA_DB_PATH)
        self.users = self.db.table('users')
        self.query = Query()

    async def update_karma(self, user_id: int, user_data: dict, delta: int) -> bool:
        try:
            user = await asyncio.to_thread(self.users.get, self.query.id == user_id)

            current_time = time.time()

            if user:
                if current_time - user.get('last_updated', 0) < 3:
                    return False

                updates = user['updates'] + [{
                    'timestamp': current_time,
                    'delta': delta
                }]

                await asyncio.to_thread(self.users.update, {
                    'total': user['total'] + delta,
                    'updates': updates,
                    'last_updated': current_time,
                    **user_data
                }, self.query.id == user_id)
            else:
                await asyncio.to_thread(self.users.insert, {
                    'id': user_id,
                    'total': delta,
                    'updates': [{
                        'timestamp': current_time,
                        'delta': delta
                    }],
                    'last_updated': current_time,
                    **user_data
                })
            return True
        except Exception as e:
            logger.exception(f"Ошибка при обновлении кармы пользователя {user_id}: {e}")
            return False

    def get_user_stats(self, user_id: int):
        try:
            user = self.users.get(self.query.id == user_id)
            if not user:
                return None

            now = time.time()
            return {
                'total': user['total'],
                'today': self._calculate_period(user['updates'], 86400),
                'week': self._calculate_period(user['updates'], 604800),
                'month': self._calculate_period(user['updates'], 2592000)
            }
        except Exception as e:
            logger.exception(f"Ошибка при получении статистики пользователя {user_id}: {e}")
            return None

    def _calculate_period(self, updates, period):
        cutoff = time.time() - period
        return sum(u['delta'] for u in updates if u['timestamp'] >= cutoff)