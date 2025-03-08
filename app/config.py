import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    GROUP_ID = int(os.getenv("GROUP_ID"))
    ALLOWED_TOPIC_ID = int(os.getenv("ALLOWED_TOPIC_ID"))
    ALLOWED_TOPIC_URL = os.getenv("ALLOWED_TOPIC_URL")
    ALLOWED_IDS = set(map(int, os.getenv("ALLOWED_IDS").split(",")))

    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_DAILY_LIMIT = int(os.getenv("DEEPSEEK_DAILY_LIMIT", 5))  # Бесплатный лимит
    
    # Пути для Docker volume
    PREDICTIONS_FILE = Path(os.getenv("PREDICTIONS_FILE", "/data/predictions.json"))
    KARMA_DB_PATH = Path(os.getenv("KARMA_DB", "/data/karma.json"))
    
    GRATITUDE_KEYWORDS = {...}  # ваш оригинальный набор
    NEGATIVE_EXPRESSIONS = {...}