import pytest

from datetime import datetime, timedelta, UTC

from src.models.statistic_model import Statistic

from src.repositories.statistic_repository import StatisticRepository, StatName


@pytest.fixture
def statistic_repository(session):
    return StatisticRepository(session)


@pytest.fixture
async def statistic(
    statistic_repository: StatisticRepository
):
    await statistic_repository.add_statistic(
        parent_id=100001,
        key=StatName.getMarks
    )

    return await statistic_repository.get_single(parent_id=100001)


@pytest.fixture
async def statistics(
    statistic_repository: StatisticRepository
):
    await statistic_repository.add_statistic(
        parent_id=100001,
        key=StatName.getMarks
    )

    await statistic_repository.add_statistic(
        parent_id=100001,
        key=StatName.getSchedule
    )

    await statistic_repository.add_statistic(
        parent_id=100002,
        key=StatName.getMarks
    )

    await statistic_repository.add_statistic(
        parent_id=None,
        key="custom_event"
    )

    return await statistic_repository.get_multi()


@pytest.mark.asyncio
async def test_add_statistic_enum(
    statistic
):
    assert statistic is not None

    assert statistic.parent_id == 100001
    assert statistic.key == StatName.getMarks.name


@pytest.mark.asyncio
async def test_add_statistic_string(
    statistic_repository: StatisticRepository
):
    await statistic_repository.add_statistic(
        parent_id=100001,
        key="custom_action"
    )

    statistic = await statistic_repository.get_single(
        Statistic.key == "custom_action"
    )

    assert statistic is not None

    assert statistic.parent_id == 100001
    assert statistic.key == "custom_action"


@pytest.mark.asyncio
async def test_get_count_unique_users(
    statistic_repository: StatisticRepository,
    statistics
):
    count = await statistic_repository.get_count_unique_users(
        since=datetime.now(UTC) - timedelta(days=1)
    )

    assert count == 2


@pytest.mark.asyncio
async def test_get_count_unique_users_ignore_null_parent(
    statistic_repository: StatisticRepository,
    statistics
):
    count = await statistic_repository.get_count_unique_users(
        since=datetime.now(UTC) - timedelta(days=1)
    )

    assert count != 3


@pytest.mark.asyncio
async def test_get_group_statistics(
    statistic_repository: StatisticRepository,
    statistics
):
    result = await statistic_repository.get_group_statistics(
        since=datetime.now(UTC) - timedelta(days=1)
    )

    stats = {
        key: count
        for key, count in result
    }

    assert stats[StatName.getMarks.name] == 2
    assert stats[StatName.getSchedule.name] == 1
    assert stats["custom_event"] == 1


@pytest.mark.asyncio
async def test_get_group_statistics_since_filter(
    statistic_repository: StatisticRepository,
    statistics
):
    result = await statistic_repository.get_group_statistics(
        since=datetime.now(UTC) + timedelta(days=1)
    )

    assert result == []
