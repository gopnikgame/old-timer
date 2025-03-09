import asyncio
import logging
from datetime import datetime
from tinydb import TinyDB, Query
from pathlib import Path
import random
from app.config import Config

logger = logging.getLogger(__name__)

class PredictionManager:
    def __init__(self):
        self.db = TinyDB(Config.PREDICTIONS_FILE)
        self.predictions = self.db.table('predictions')
        self.query = Query()

    async def get_prediction(self):
        try:
            available = await asyncio.to_thread(self.predictions.search, self.query.used == False)
            if not available:
                await self._reset_predictions()
                available = await asyncio.to_thread(self.predictions.all)

            if not available:
                logger.warning("Нет доступных предсказаний.")
                return "🔮 Нет предсказаний."

            prediction = random.choice(available)
            await asyncio.to_thread(self.predictions.update, {'used': True}, doc_ids=[prediction.doc_id])
            return prediction['text']
        except Exception as e:
            logger.exception("Ошибка при получении предсказания.")
            return "🔮 Ошибка предсказания."

    async def _reset_predictions(self):
        try:
            await asyncio.to_thread(self.predictions.update, {'used': False})
        except Exception as e:
            logger.exception("Ошибка при сбросе предсказаний.")

    def add_prediction(self, text: str):
        try:
            self.predictions.insert({
                'text': text,
                'used': False,
                'created_at': datetime.now().isoformat()
            })
        except Exception as e:
            logger.exception(f"Ошибка при добавлении предсказания: {text}")