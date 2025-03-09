import os
from dotenv import load_dotenv
from pathlib import Path
import logging

load_dotenv()

logger = logging.getLogger(__name__)

class Config:
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    GROUP_ID = os.getenv("GROUP_ID")
    ALLOWED_TOPIC_ID = os.getenv("ALLOWED_TOPIC_ID")
    ALLOWED_TOPIC_URL = os.getenv("ALLOWED_TOPIC_URL")
    ALLOWED_IDS = os.getenv("ALLOWED_IDS")

    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
    DEEPSEEK_DAILY_LIMIT = os.getenv("DEEPSEEK_DAILY_LIMIT", "5")

    # PostgreSQL Configuration
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "botdb")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db") # Use the service name from docker-compose.yml

    # Проверка наличия обязательных переменных
    if not all([BOT_TOKEN, GROUP_ID, ALLOWED_TOPIC_ID, ALLOWED_TOPIC_URL, ALLOWED_IDS]):
        logger.error("Не заданы обязательные переменные окружения!")
        raise ValueError("Не заданы обязательные переменные окружения!")

    try:
        GROUP_ID = int(GROUP_ID)
        ALLOWED_TOPIC_ID = int(ALLOWED_TOPIC_ID)
        ALLOWED_IDS = set(map(int, ALLOWED_IDS.split(",")))
        DEEPSEEK_DAILY_LIMIT = int(DEEPSEEK_DAILY_LIMIT)
        PREDICTIONS_FILE = Path(PREDICTIONS_FILE)
        KARMA_DB_PATH = Path(KARMA_DB_PATH)
    except ValueError as e:
        logger.error(f"Ошибка приведения типов переменных окружения: {e}")
        raise

    GRATITUDE_KEYWORDS = {
        "спасибо", "спс", "сяп", "пасиб",
        "спасибки", "спасиба", "сяб", "пасибки", "благодарю",
        "благодарствую", "благодарочка", "благодарность", "признателен", "признательна",
        "молодец конечно", "супер как всегда", "респект", "респектище", "уважуха",
        "красава", "красавчик", "умничка", "ты жжёшь", "чмок",
        "обнимашки", "герой", "спаситель", "бог чата", "легенда",
        "мастер", "чемпион", "царь", "босс", "титан",
        "гуру", "боженька", "превед", "огонь", "шикарно",
        "мегаспасибо", "гигаспасибо", "суперспасибо", "огромное спасибо", "огромнейшее спасибо",
        "thanks", "thx", "merci", "danke", "gracias",
        "arigato", "дякую", "сенкс", "мерси", "sps",
        "spasibo", "blag", "thnx", "thanx", "grats",
        "ty", "обожаю", "обнимаю", "целую", "люблю",
        "ты лучший", "ты лучшая", "ты космос", "ты гений", "плюс",
        "+", "норм", "нормально", "неплохо", "сойдёт",
        "приемлемо", "достойно", "хорошо", "отлично", "классно",
        "круто", "супер", "топ", "годно", "полезно",
        "лайк", "достойно уважения", "по кайфу", "великолепно", "невероятно",
        "бомба", "идеально", "потрясающе", "гениально", "мастерски",
        "восхитительно", "это база", "ты жёшь"
    }

    NEGATIVE_EXPRESSIONS = {
        "минус тебе", "минус", "дизлайк", "понижаю карму", "чёрная метка",
        "отстой", "ненавижу", "бесишь", "уйди", "исчезни",
        "заткнись", "надоел", "достал", "отвратительно", "фигня",
        "хрень", "лажа", "кошмар", "ужас", "отстойно",
        "плохо", "отвратно", "умник нашёлся", "гений блин",
        "не очень", "слабовато", "так себе", "посредственно",
        "ниже среднего", "можно лучше", "брабус"
    }