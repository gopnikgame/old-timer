import logging

from app.db.database import db

logger = logging.getLogger(__name__)

async def get_karma(user_id: int) -> int:
    try:
        record = await db.fetchone("SELECT karma FROM karma WHERE user_id = $1", user_id)
        if record:
            return record['karma']
        return 0
    except Exception as e:
        logger.exception(f"Error getting karma for user {user_id}: {e}")
        return 0

async def update_karma(user_id: int, change: int):
    try:
        await db.execute(
            """
            INSERT INTO karma (user_id, karma)
            VALUES ($1, $2)
            ON CONFLICT (user_id) DO UPDATE SET karma = karma + $2
            """,
            user_id,
            change
        )
    except Exception as e:
        logger.exception(f"Error updating karma for user {user_id} with change {change}: {e}")

async def get_top_karma(limit: int = 10):
    try:
        records = await db.fetchmany(
            "SELECT user_id, karma FROM karma ORDER BY karma DESC",
            limit=limit
        )
        return records
    except Exception as e:
        logger.exception(f"Error getting top karma: {e}")
        return []

async def get_bottom_karma(limit: int = 10):
    try:
        records = await db.fetchmany(
            "SELECT user_id, karma FROM karma ORDER BY karma ASC",
            limit=limit
        )
        return records
    except Exception as e:
        logger.exception(f"Error getting bottom karma: {e}")
        return []