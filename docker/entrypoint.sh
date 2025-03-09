#!/bin/sh

# Копирование файла предсказаний, если он не существует
if [ ! -f "$PREDICTIONS_FILE" ]; then
    echo "Файл $PREDICTIONS_FILE не найден. Копирую из /app/data/predictions.json"
    cp /app/data/predictions.json "$PREDICTIONS_FILE"
    if [ $? -ne 0 ]; then
        echo "Ошибка при копировании файла предсказаний!"
        exit 1
    fi
fi

# Запуск бота
echo "Запуск бота..."
exec python -m app.bot