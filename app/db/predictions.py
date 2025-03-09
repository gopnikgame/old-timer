import logging
import random

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

async def get_prediction():
    try:
        # Get available prediction
        record = await db.fetchone("SELECT id, user_id, prediction_text FROM predictions LIMIT 1")
        if record:
            prediction = record['prediction_text']
            prediction_id = record['id']
            # Archive used prediction
            await archive_prediction(record['user_id'], record['prediction_text'])
            # Remove used prediction
            await db.execute("DELETE FROM predictions WHERE id = $1", prediction_id)
            return prediction

        # Refill predictions from archive
        await refill_predictions()

        # Get prediction after refill
        record = await db.fetchone("SELECT id, user_id, prediction_text FROM predictions LIMIT 1")
        if record:
            prediction = record['prediction_text']
            prediction_id = record['id']
            # Archive used prediction
            await archive_prediction(record['user_id'], record['prediction_text'])
            # Remove used prediction
            await db.execute("DELETE FROM predictions WHERE id = $1", prediction_id)
            return prediction
        
        return "🔮 Нет предсказаний."
    except Exception as e:
        logger.exception(f"Error getting prediction: {e}")
        return "🔮 Ошибка при получении предсказания."

async def refill_predictions():
    try:
        # Get all archived predictions
        records = await db.fetchmany("SELECT user_id, prediction_text FROM predictions_archive")
        if not records:
            logger.info("No archived predictions to refill.")
            return

        # Insert archived predictions back to predictions table
        for record in records:
            await db.execute(
                """
                INSERT INTO predictions (user_id, prediction_text)
                VALUES ($1, $2)
                """,
                record['user_id'],
                record['prediction_text']
            )
        
        # Clear archive
        await db.execute("DELETE FROM predictions_archive")
        logger.info("Predictions refilled from archive.")
    except Exception as e:
        logger.exception(f"Error refilling predictions: {e}")

async def archive_prediction(user_id: int, prediction_text: str):
     try:
        await db.execute(
            """
            INSERT INTO predictions_archive (user_id, prediction_text)
            VALUES ($1, $2)
            """,
            user_id,
            prediction_text
        )
        logger.info(f"Prediction archived for user {user_id}")
     except Exception as e:
        logger.exception(f"Error archiving prediction for user {user_id}: {e}")