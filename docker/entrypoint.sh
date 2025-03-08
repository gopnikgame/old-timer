#!/bin/sh

if [ ! -f "$PREDICTIONS_FILE" ]; then
    cp /app/data/predictions.json $PREDICTIONS_FILE
fi

exec python -m app.bot