#!/bin/sh

# Останавливать скрипт при любой ошибке
set -e

echo "Применение миграций Alembic..."
alembic upgrade head

echo "Запуск тестов..."
exec pytest tests
