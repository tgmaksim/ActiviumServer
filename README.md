<br>

<div align="center">
    <img src="www/assets/icons/preview.png" width="200" style="border-radius: 20%" alt="Activium Server" />
</div>

<h1 align="center">Activium Server</h1>
<p align="center">
    <b>Серверная часть приложения «Активиум» с Activium API, фоновыми процессами, Telegram-ботом и сайтом</b>
</p>
<br>

<div align="center">
    <img alt="Python 3.12" src="https://img.shields.io/badge/python-3.12-blue?logo=python&logoColor=ffdd54" />
    <img alt="GNU GPL v3" src="https://img.shields.io/badge/license-%20%20GNU%20GPLv3%20-blue" />
</div>

<div align="center">
    <img alt="Docker" src="https://img.shields.io/badge/Docker-2496ED?logo=docker&logoColor=white" />
    <img alt="FastAPI" src="https://img.shields.io/badge/-FastAPI-blue?logo=fastapi&logoColor=white" />
    <img alt="PostgreSQL" src="https://img.shields.io/badge/-PostgreSQL-blue?logo=postgresql&logoColor=white" />
    <img alt="Pydantic" src="https://img.shields.io/badge/-Pydantic-blue?logo=pydantic&logoColor=white" />
    <img alt="Pytest" src="https://img.shields.io/badge/-Pytest-blue?logo=pytest&logoColor=white" />
    <img alt="Firebase" src="https://img.shields.io/badge/-Firebase-blue?logo=firebase&logoColor=white" />
</div>
<br>

## 📱 Мобильное приложение
Полная реализация возможностей сервера доступна в мобильном приложении «Активиум»
https://github.com/tgmaksim/Activium

## 🌐 Сайт
Официальный сайт доступен по адресу https://activium.tgmaksim.ru

## 🛠 Технологии
- [x] Python 3.12
- [x] FastAPI
- [x] Pydantic
- [x] Docker
- [x] SQLAlchemy 2.x (async)
- [x] Alembic
- [x] PostgreSQL
- [x] Pytest
- [x] Aiogram
- [x] Firebase

## 📦 Структура каталогов
- **src** — Основное приложение FastAPI
  - src.config — Конфигурация проекта, OpenAPI и настройки базы данных
  - src.dependencies — Зависимости FastAPI
  - src.middlewares — Промежуточное ПО для мониторинга, валидации и логирования
  - src.models, src.schemas — Модели SQLAlchemy и схемы Pydantic
- **backgrounds**, **crons** — Фоновые задачи и периодические скрипты для работы уведомлений, статистики и других задач
- **dnevnikru** — SDK для интеграции с API Дневника.ру
- **ai** — SDK для интеграции OpenRouter API
- **firebase** — SDK для интеграции с API Firebase
- **tgbot** — Telegram-бот для администрирования образовательных организаций
- **tests** — Тестирование с Pytest
- **templates** — Шаблоны HTML для сайта и школьных постов
- **www** — Статические файлы для сайта, школьных постов и картинок уведомлений

## 🚀 Быстрый запуск

1. Установить Docker
2. Скопировать репозиторий и открыть директорию
    ```bash
    git clone https://github.com/tgmaksim/ActiviumServer
    cd ActiviumServer
    ```
3. Переименовать файлы-шаблоны
    ```bash
    cp .example.env .env
    cp .example.debug.env .debug.env
    cp .example.tests.env .test.env
    cp firebase-adminsdk.example.json firebase-adminsdk.json
    cp alembic.example.ini alembic.ini
   ```
4. Для локального запуска заменить ключи в .debug.env
    ```dotenv
    DNEVNIK_CLIENT_ID=key
    OPENAI_URL=https://example.com/v1  # Необязательно
    OPENAI_API_KEY=key  # Необязательно

    BOT_TOKEN=bot_id:token  # API-ключ бота от @BotFather
    ADMIN_CHAT_IDS='[0]'  # User_id пользователя с правами администратора в боте
    BOT_URL=https://t.me/username  # Заменить на username бота
    START_TGBOT_WORKER=0  # Или выключить бота
    ```
5. Для работы уведомлений на клиентское приложение заменить конфигурацию в firebase-adminsdk.json
6. Запустить Docker
    ```bash
    docker-compose up --build
    ```
После запуска 
- pgadmin доступен по адресу http://localhost:5050 с admin@admin.com admin_password
- база данных на postgres_db с db_user db_password
- Сайт и сервер доступны по адресу http://localhost:8000
- Документация Activium API - Swagger доступна по адресу http://localhost:8000/api/v2/docs

## 🚀 Быстрый запуск тестов

1. Установить Docker
2. Скопировать репозиторий и открыть директорию
    ```bash
    git clone https://github.com/tgmaksim/ActiviumServer
    cd ActiviumServer
    ```
3. Переименовать файлы-шаблоны
    ```bash
    cp .example.env .env
    cp .example.debug.env .debug.env
    cp .example.tests.env .tests.env
    cp firebase-adminsdk.example.json firebase-adminsdk.json
    cp alembic.example.ini alembic.ini
   ```
4. Запустить тесты в Docker
    ```bash
    docker-compose -f docker-compose.test.yml up --build
    ```

> [!NOTE]
> Для production-запуска также требуется настроить NGINX для передачи статических файлов из папки www

## 📄 Лицензия
Проект распространяет под лицензией GNU GPL v3
