# 🤖 Old-Timer Bot | Бот-Старожил

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Python](https://img.shields.io/badge/python-3.9+-yellow)
![aiogram](https://img.shields.io/badge/aiogram-3.0+-orange)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13-blue)

## 📜 О проекте | About

Old-Timer - это многофункциональный Telegram бот для групповых чатов с системой кармы, предсказаниями и другими полезными функциями. Создан для улучшения взаимодействия пользователей в тематических группах.

*Old-Timer is a multifunctional Telegram bot for group chats with a karma system, predictions, and other useful features. Created to enhance user interaction in topic-based groups.*

## ✨ Возможности | Features

- 🏆 **Система кармы**: Отслеживание рейтинга пользователей
- 🔮 **Предсказания**: Персонализированные предсказания с использованием DeepSeek AI
- 🛡️ **Модерация тем**: Контроль использования команд в определенных топиках
- 📊 **Рейтинги**: Отображение топ пользователей по карме
- 🚀 **Docker интеграция**: Простое развертывание с Docker Compose
- 🔄 **Автоматическое обновление**: Скрипт для обновления бота из репозитория

## 🛠 Технологии | Technologies

- **Python 3.9+**: Основной язык программирования
- **aiogram 3.0+**: Фреймворк для Telegram Bot API
- **PostgreSQL**: База данных для хранения информации
- **Docker & Docker Compose**: Контейнеризация и удобное развертывание
- **DeepSeek API**: Генерация текста для предсказаний
- **asyncpg**: Асинхронная работа с PostgreSQL

## 📋 Требования | Requirements

```
aiogram>=3.0
python-dotenv>=0.19
aiofiles>=22.1
python-multipart>=0.0.5
httpx>=0.23
asyncpg>=0.29.0
```

## 🚀 Установка и запуск | Installation & Running

### 🏗 Быстрая установка | Quick Setup

```bash
curl -sSL https://raw.githubusercontent.com/gopnikgame/old-timer/main/launcher.sh | sudo bash
```

### 🔧 Ручная установка | Manual Setup

1. Клонировать репозиторий:
```bash
git clone https://github.com/gopnikgame/old-timer.git
cd old-timer
```

2. Скопировать `.env.example` в `.env` и настроить параметры:
```bash
cp .env.example .env
nano .env
```

3. Запустить с Docker Compose:
```bash
docker-compose up -d
```

## ⚙️ Конфигурация | Configuration

Создайте файл `.env` на основе `.env.example` и укажите следующие параметры:

| Параметр | Описание |
|---------|----------|
| `BOT_TOKEN` | Токен от BotFather |
| `GROUP_ID` | ID вашей группы в Telegram |
| `ALLOWED_TOPIC_ID` | ID топика, где разрешены команды |
| `ALLOWED_TOPIC_URL` | URL топика, где разрешены команды |
| `ALLOWED_IDS` | ID администраторов, через запятую |
| `DEEPSEEK_API_KEY` | API ключ для DeepSeek |
| `DEEPSEEK_DAILY_LIMIT` | Дневной лимит запросов к API |
| `POSTGRES_*` | Настройки подключения к PostgreSQL |

## 🤝 Команды бота | Bot Commands

- `/help` - Показать список доступных команд
- `/future` - Получить персональное предсказание
- `/karma` - Показать вашу карму
- `/topkarma` - Топ пользователей по карме
- `/antikarma` - Топ антикармы
- `/add_prediction [текст]` - Добавить новое предсказание (только для админов)

## 📊 Структура базы данных | Database Structure

```sql
-- Таблица karma
CREATE TABLE IF NOT EXISTS karma (
    user_id BIGINT PRIMARY KEY,
    karma INT NOT NULL DEFAULT 0
);

-- Таблица predictions
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    prediction_text TEXT NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() at time zone 'utc')
);

-- Таблица predictions_archive
CREATE TABLE IF NOT EXISTS predictions_archive (
    user_id BIGINT NOT NULL,
    prediction_text TEXT NOT NULL
);

-- Таблица karma_updates
CREATE TABLE IF NOT EXISTS karma_updates (
    user_id BIGINT NOT NULL,
    karma INT NOT NULL,
    timestamp DOUBLE PRECISION NOT NULL
);
```

## 📁 Структура проекта | Project Structure

```
old-timer/
├── app/
│   ├── __init__.py
│   ├── bot.py
│   ├── config.py
│   ├── db/
│   │   ├── database.py
│   │   ├── karma.py
│   │   └── predictions.py
│   ├── handlers/
│   │   ├── base.py
│   │   └── ...
│   ├── middlewares/
│   │   ├── logging.py
│   │   └── topic_check.py
│   └── utils/
│       └── formatting.py
├── data/
│   └── initial_predictions.json
├── scripts/
│   └── manage_bot.sh
├── docker/
├── launcher.sh
├── docker-compose.yml
├── Dockerfile
├── db_schema.sql
├── .env.example
└── README.md
```

## ⚠️ Антиспам система | Anti-spam System

Бот включает встроенную защиту от спама для системы кармы:
- Ограничение на изменение кармы одному пользователю (не чаще чем раз в 3 секунды)
- Логирование всех обновлений кармы с временными метками

## 📄 Лицензия | License

Распространяется под лицензией MIT. Смотрите файл `LICENSE` для получения дополнительной информации.

## 👨‍💻 Авторы | Authors

- **GopnikGame** - *Создатель проекта* - [GitHub](https://github.com/gopnikgame)

## 🔄 Последнее обновление | Last Updated

Дата: 2025-03-09

---

Сделано с ❤️ для Telegram сообществ