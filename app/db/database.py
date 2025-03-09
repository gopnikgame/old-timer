import asyncio
import logging
import json

import asyncpg

from app.config import Config

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.pool = None

    async def create_pool(self):
        try:
            self.pool = await asyncpg.create_pool(
                user=Config.POSTGRES_USER,
                password=Config.POSTGRES_PASSWORD,
                database=Config.POSTGRES_DB,
                host=Config.POSTGRES_HOST
            )
            logger.info("Database pool created")
        except Exception as e:
            logger.exception("Error creating database pool")
            raise

    async def execute(self, query, *args):
        async with self.pool.acquire() as conn:
            try:
                await conn.execute(query, *args)
            except Exception as e:
                logger.exception(f"Error executing query: {query} with args: {args}")
                raise

    async def fetchone(self, query, *args):
        async with self.pool.acquire() as conn:
            try:
                return await conn.fetchrow(query, *args)
            except Exception as e:
                logger.exception(f"Error fetching one: {query} with args: {args}")
                raise

    async def fetchmany(self, query, *args, limit=None):
         async with self.pool.acquire() as conn:
            try:
                return await conn.fetch(query, *args, limit=limit)
            except Exception as e:
                logger.exception(f"Error fetching many: {query} with args: {args}")
                raise

    async def close(self):
        if self.pool:
            await self.pool.close()
            logger.info("Database pool closed")

    async def create_tables(self):
        async with self.pool.acquire() as conn:
            try:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS karma (
                        user_id BIGINT PRIMARY KEY,
                        karma INT NOT NULL DEFAULT 0
                    )
                """)
                logger.info("Karma table created (if not exists)")
            except Exception as e:
                logger.exception("Error creating karma table")
                raise

    async def create_predictions_table(self):
        async with self.pool.acquire() as conn:
            try:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS predictions (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT NOT NULL,
                        prediction_text TEXT NOT NULL,
                        created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (NOW() at time zone 'utc')
                    )
                """)
                logger.info("Predictions table created (if not exists)")

                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS predictions_archive (
                        user_id BIGINT NOT NULL,
                        prediction_text TEXT NOT NULL
                    )
                """)
                logger.info("predictions_archive table created (if not exists)")
            except Exception as e:
                logger.exception("Error creating predictions table")
                raise

    async def create_karma_updates_table(self):
        async with self.pool.acquire() as conn:
            try:
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS karma_updates (
                        user_id BIGINT NOT NULL,
                        karma INT NOT NULL,
                        timestamp DOUBLE PRECISION NOT NULL
                    )
                """)
                logger.info("karma_updates table created (if not exists)")
            except Exception as e:
                logger.exception("Error creating karma_updates table")
                raise

    async def check_initial_predictions_inserted(self):
        try:
            record = await self.fetchone("SELECT COUNT(*) FROM predictions")
            if record:
                return record['count'] > 0
            return False
        except Exception as e:
            logger.exception(f"Error checking initial predictions: {e}")
            return False

    async def insert_initial_predictions(self, file_path: str):
        try:
            with open(file_path, 'r') as f:
                predictions = json.load(f)

            for prediction in predictions:
                user_id = prediction['user_id']
                prediction_text = prediction['prediction_text']
                await self.execute(
                    """
                    INSERT INTO predictions (user_id, prediction_text)
                    VALUES ($1, $2)
                    """,
                    user_id,
                    prediction_text
                )
            logger.info(f"Initial predictions inserted from {file_path}")
        except Exception as e:
            logger.exception(f"Error inserting initial predictions from {file_path}: {e}")

# Создаем экземпляр базы данных
db = Database()

async def init_db():
    await db.create_pool()
    await db.create_tables()
    await db.create_predictions_table()
    await db.create_karma_updates_table()

    # Check if initial predictions are already inserted
    if not await db.check_initial_predictions_inserted():
        await db.insert_initial_predictions(Config.INITIAL_PREDICTIONS_FILE)