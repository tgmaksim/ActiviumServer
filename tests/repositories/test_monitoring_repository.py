import pytest

from datetime import datetime, timedelta, UTC

from src.repositories.monitoring_repository import MonitoringRepository


@pytest.mark.asyncio
async def test_add_monitoring(
    monitoring
):
    assert monitoring is not None

    assert monitoring.path == "/api/test"
    assert monitoring.session_id == "session_1"
    assert monitoring.status is True

    assert monitoring.duration == timedelta(milliseconds=250)


@pytest.mark.asyncio
async def test_get_stats(
    monitoring_repository: MonitoringRepository,
    monitorings
):
    stats = await monitoring_repository.get_stats(
        since=datetime.now(UTC) - timedelta(days=1)
    )

    assert len(stats) == 2

    stats_by_path = {
        path: (min_duration, max_duration, median_duration)
        for path, min_duration, max_duration, median_duration in stats
    }

    users_stats = stats_by_path["/api/users"]

    assert users_stats[0] == timedelta(milliseconds=100)
    assert users_stats[1] == timedelta(milliseconds=300)
    assert users_stats[2] == timedelta(milliseconds=200)

    posts_stats = stats_by_path["/api/posts"]

    assert posts_stats[0] == timedelta(milliseconds=200)
    assert posts_stats[1] == timedelta(milliseconds=200)
    assert posts_stats[2] == timedelta(milliseconds=200)


@pytest.mark.asyncio
async def test_get_stats_ignore_failed_requests(
    monitoring_repository: MonitoringRepository,
    monitorings
):
    stats = await monitoring_repository.get_stats(
        since=datetime.now(UTC) - timedelta(days=1)
    )

    stats_by_path = {
        path: (min_duration, max_duration, median_duration)
        for path, min_duration, max_duration, median_duration in stats
    }

    users_stats = stats_by_path["/api/users"]

    assert users_stats[1] != timedelta(milliseconds=500)


@pytest.mark.asyncio
async def test_get_stats_since_filter(
    monitoring_repository: MonitoringRepository,
    monitorings
):
    stats = await monitoring_repository.get_stats(
        since=datetime.now(UTC) + timedelta(days=1)
    )

    assert stats == []
