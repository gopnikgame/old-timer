import asyncio
import logging

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

# Создаем экземпляр базы данных
db = Database()

async def init_db():
    await db.create_pool()