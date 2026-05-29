import pytest

from src.models.log_model import Log

from src.repositories.log_repository import LogRepository


@pytest.mark.asyncio
async def test_add_log(
    log: Log
):
    assert log.log_id is not None
    assert log.ip == "127.0.0.1"
    assert log.path == "/api/test"
    assert log.session_id == "session_1"
    assert log.status is True
    assert log.method == "GET"
    assert log.value == "Success"


@pytest.mark.asyncio
async def test_add_log_nullable_fields(
    log_repository: LogRepository
):
    log = await log_repository.add_log(
        path="scheduler.task",
        value="Task completed"
    )

    assert log.ip is None
    assert log.session_id is None
    assert log.method is None
    assert log.status is True
