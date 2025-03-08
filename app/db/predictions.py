from datetime import datetime
from tinydb import TinyDB, Query
from pathlib import Path
import random
from app.config import Config

class PredictionManager:
    def __init__(self):
        self.db = TinyDB(Config.PREDICTIONS_FILE)
        self.predictions = self.db.table('predictions')
        self.query = Query()

    async def get_prediction(self):
        available = self.predictions.search(self.query.used == False)
        if not available:
            self._reset_predictions()
            available = self.predictions.all()
            
        prediction = random.choice(available)
        self.predictions.update({'used': True}, doc_ids=[prediction.doc_id])
        return prediction['text']

    def _reset_predictions(self):
        self.predictions.update({'used': False})

    def add_prediction(self, text: str):
        self.predictions.insert({
            'text': text,
            'used': False,
            'created_at': datetime.now().isoformat()
        })