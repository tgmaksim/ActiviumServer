FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Установка русской локали для python datetime
RUN apt-get update && apt-get install -y --no-install-recommends \
    locales \
    && sed -i -e 's/# ru_RU.UTF-8 UTF-8/ru_RU.UTF-8 UTF-8/' /etc/locale.gen \
    && locale-gen \
    && rm -rf /var/lib/apt/lists/*

# Копирвоание зависимостей
COPY requirements.txt .

# Обновление pip и установка зависимостей
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Копируются все файлы и директории в app, кроме статических файлов в www (из-за dockerignore)
COPY . .
RUN rm -rf www

# Статические файлы в www находятся в корне
COPY ./www /www

# Права на выполнение entrypoint.sh и tests.sh
RUN chmod +x /app/entrypoint.sh
RUN chmod +x /app/tests.sh

# Открытие порта
EXPOSE 8000

# Инциализация БД и запуск приложения
CMD ["/app/entrypoint.sh"]
