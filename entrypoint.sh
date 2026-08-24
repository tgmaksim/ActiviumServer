#!/bin/sh

# Останавливать скрипт при любой ошибке
set -e

echo "Применение миграций Alembic..."
alembic upgrade head

echo "Запуск сервера Uvicorn..."
exec uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
