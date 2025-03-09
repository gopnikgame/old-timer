import logging
import time
import datetime

from app.db.database import db

logger = logging.getLogger(__name__)

LAST_UPDATE_TIMES = {}  # Словарь для хранения времени последнего обновления кармы

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
    global LAST_UPDATE_TIMES
    now = time.time()
    last_updated = LAST_UPDATE_TIMES.get(user_id, 0)

    if now - last_updated < 3:
        logger.info(f"Skipped karma update for user {user_id} (antispam)")
        return False

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
        await db.execute(
            """
            INSERT INTO karma_updates (user_id, karma, timestamp)
            VALUES ($1, $2, $3)
            """,
            user_id,
            change,
            now
        )
        LAST_UPDATE_TIMES[user_id] = now
        return True
    except Exception as e:
        logger.exception(f"Error updating karma for user {user_id} with change {change}: {e}")
        return False

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

async def compute_period_karma(user_id: int, start_ts: float, end_ts: float) -> int:
    try:
        records = await db.fetchmany(
            """
            SELECT karma FROM karma_updates 
            WHERE user_id = $1 AND timestamp >= $2 AND timestamp < $3
            """,
            user_id,
            start_ts,
            end_ts
        )
        return sum(record['karma'] for record in records)
    except Exception as e:
        logger.exception(f"Error computing period karma for user {user_id}: {e}")
        return 0