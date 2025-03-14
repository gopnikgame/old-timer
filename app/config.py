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

    # GigaChat API конфигурация
    GIGACHAT_CLIENT_ID = os.getenv("GIGACHAT_CLIENT_ID")
    GIGACHAT_CLIENT_SECRET = os.getenv("GIGACHAT_CLIENT_SECRET")
    GIGACHAT_SCOPE = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")
    GIGACHAT_BASE_URL = os.getenv("GIGACHAT_BASE_URL", "https://gigachat.devices.sberbank.ru/api/v1")
    GIGACHAT_AUTH_URL = os.getenv("GIGACHAT_AUTH_URL", "https://ngw.devices.sberbank.ru:9443/api/v2/oauth")
    GIGACHAT_DAILY_LIMIT = os.getenv("GIGACHAT_DAILY_LIMIT", "5")

    # PostgreSQL Configuration
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB = os.getenv("POSTGRES_DB", "botdb")
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "db") # Use the service name from docker-compose.yml
    INITIAL_PREDICTIONS_FILE = os.getenv("INITIAL_PREDICTIONS_FILE", "/app/data/initial_predictions.json")

    # Проверка наличия обязательных переменных
    # Уберем ALLOWED_TOPIC_ID и ALLOWED_TOPIC_URL из обязательных переменных
    if not all([BOT_TOKEN, GROUP_ID, ALLOWED_IDS]):
        logger.error("Не заданы обязательные переменные окружения!")
        raise ValueError("Не заданы обязательные переменные окружения!")

    try:
        GROUP_ID = int(GROUP_ID)
        # Если ALLOWED_TOPIC_ID указан, преобразуем его в число
        if ALLOWED_TOPIC_ID:
            ALLOWED_TOPIC_ID = int(ALLOWED_TOPIC_ID)
        else:
            # Если ALLOWED_TOPIC_ID не указан, устанавливаем его в None
            ALLOWED_TOPIC_ID = None
            
        ALLOWED_IDS = set(map(int, ALLOWED_IDS.split(",")))
        GIGACHAT_DAILY_LIMIT = int(GIGACHAT_DAILY_LIMIT)
    except ValueError as e:
        logger.error(f"Ошибка приведения типов переменных окружения: {e}")
        raise

    # Если URL топика не указан, используем заглушку
    if not ALLOWED_TOPIC_URL:
        ALLOWED_TOPIC_URL = "этот чат"


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