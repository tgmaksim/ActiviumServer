import pytest
import asyncio

from sqlalchemy.ext.asyncio import (
    async_sessionmaker,
    create_async_engine,
)

from src.config.database.db_config import settings_db

from src.repositories.db_queue import AsyncDBQueue


engine = create_async_engine(settings_db.database_url, echo=settings_db.DB_ECHO)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    """Создает один Event Loop на всю сессию тестирования"""

    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()

    yield loop

    loop.close()


@pytest.fixture
async def session():
    async with engine.connect() as connection:
        transaction = await connection.begin()

        session = SessionLocal(bind=connection)
        db_queue = AsyncDBQueue(session)

        try:
            await db_queue.start()
            yield db_queue

        finally:
            await db_queue.stop()
            await session.close()
            await transaction.rollback()
