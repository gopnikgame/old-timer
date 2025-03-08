import time  # Добавляем импорт модуля
from datetime import datetime, timedelta
from tinydb import TinyDB, Query
from pathlib import Path
from app.config import Config

class KarmaManager:
    def __init__(self):
        self.db = TinyDB(Config.KARMA_DB_PATH)
        self.users = self.db.table('users')
        self.query = Query()

    async def update_karma(self, user_id: int, user_data: dict, delta: int) -> bool:
        user = self.users.get(self.query.id == user_id)
        
        current_time = time.time()  # Теперь time доступен
        
        if user:
            if current_time - user.get('last_updated', 0) < 3:
                return False
            
            updates = user['updates'] + [{
                'timestamp': current_time,
                'delta': delta
            }]
            
            self.users.update({
                'total': user['total'] + delta,
                'updates': updates,
                'last_updated': current_time,
                **user_data
            }, self.query.id == user_id)
        else:
            self.users.insert({
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

    def get_user_stats(self, user_id: int):
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

    def _calculate_period(self, updates, period):
        cutoff = time.time() - period
        return sum(u['delta'] for u in updates if u['timestamp'] >= cutoff)