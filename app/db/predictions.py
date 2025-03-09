import logging

from app.db.database import db

logger = logging.getLogger(__name__)

async def add_prediction(user_id: int, prediction_text: str):
    try:
        await db.execute(
            """
            INSERT INTO predictions (user_id, prediction_text)
            VALUES ($1, $2)
            """,
            user_id,
            prediction_text
        )
        logger.info(f"Prediction added for user {user_id}")
    except Exception as e:
        logger.exception(f"Error adding prediction for user {user_id}: {e}")

async def get_predictions(user_id: int, limit: int = 10):
    try:
        records = await db.fetchmany(
            "SELECT id, prediction_text, created_at FROM predictions WHERE user_id = $1 ORDER BY created_at DESC",
            user_id,
            limit=limit
        )
        return records
    except Exception as e:
        logger.exception(f"Error getting predictions for user {user_id}: {e}")
        return []