import pytest

from types import SimpleNamespace

from unittest.mock import patch, AsyncMock

from src.repositories.statistic_repository import StatName
from src.support.services.status_service import StatusService
from src.support.schemas.status_schemas import (
    VersionsResult,
    HealthApiResponse,
    VersionsResult0x3,
    VersionsApiResponse,
    VersionsApiResponse0x4,
)


@pytest.fixture
def status_service(uow_factory):
    return StatusService(uow_factory)


@pytest.fixture
def mock_status_check_session(fake_session):
    with patch(
        "src.support.services.status_service.check_session",
        new=AsyncMock(return_value=fake_session)
    ) as mock:
        yield mock


@pytest.fixture
def information():
    return SimpleNamespace(
        type="common",
        title="Title",
        text="Text"
    )


@pytest.fixture
def review_information():
    return SimpleNamespace(
        type="review",
        title="Review title",
        text="Review text"
    )


@pytest.fixture
def review():
    return SimpleNamespace()


@pytest.fixture
def marks_notification_information():
    return SimpleNamespace(
        type="marks_notifications",
        title="Marks title",
        text="Marks text"
    )


@pytest.fixture
def marks_notification():
    return SimpleNamespace()


@pytest.mark.asyncio
async def test_health(status_service):
    result = await status_service.health()

    assert isinstance(result, HealthApiResponse)
    assert result.status is True
    assert result.error is None


@pytest.mark.asyncio
async def test_check_latest_version_old_api_schema(
    fake_uow,
    status_service,
    latest_version
):
    fake_uow.version_repository.get_latest_version.return_value = latest_version
    fake_uow.version_repository.get_latest_generic_version.return_value = latest_version
    fake_uow.version_repository.get_latest_mini_versions.return_value = []
    fake_uow.version_repository.get_most_important_version.return_value = None

    result = await status_service.check_latest_version(
        latest_version.number,
        api=0
    )

    assert isinstance(result, VersionsApiResponse0x4)
    assert isinstance(result.answer, VersionsResult0x3)


@pytest.mark.asyncio
async def test_check_latest_version(
    fake_uow,
    uow_factory,
    status_service,
    latest_version
):
    fake_uow.version_repository.get_latest_version.return_value = latest_version
    fake_uow.version_repository.get_latest_generic_version.return_value = latest_version
    fake_uow.version_repository.get_latest_mini_versions.return_value = []
    fake_uow.version_repository.get_most_important_version.return_value = None

    result = await status_service.check_latest_version(
        latest_version.number
    )

    assert isinstance(result, VersionsApiResponse)
    assert isinstance(result.answer, VersionsResult)

    assert result.answer.latestVersionNumber == latest_version.number
    assert result.answer.latestVersionString == latest_version.version
    assert result.answer.versionStatusId == latest_version.status_id
    assert result.answer.versionStatus == latest_version.status
    assert result.answer.info == latest_version.info
    assert result.answer.updateLogs == latest_version.logs


@pytest.mark.asyncio
async def test_check_latest_version_use_most_important(
    fake_uow,
    uow_factory,
    status_service,
    latest_version,
    important_version
):
    fake_uow.version_repository.get_latest_version.return_value = latest_version
    fake_uow.version_repository.get_latest_generic_version.return_value = latest_version
    fake_uow.version_repository.get_latest_mini_versions.return_value = []
    fake_uow.version_repository.get_most_important_version.return_value = important_version

    result = await status_service.check_latest_version(1)

    assert result.answer.versionStatusId == important_version.status_id
    assert result.answer.versionStatus == important_version.status
    assert result.answer.info == important_version.info


@pytest.mark.asyncio
async def test_check_latest_version_use_generic_logs(
    fake_uow,
    uow_factory,
    status_service,
    latest_version,
    generic_latest_version
):
    fake_uow.version_repository.get_latest_version.return_value = latest_version
    fake_uow.version_repository.get_latest_generic_version.return_value = generic_latest_version
    fake_uow.version_repository.get_latest_mini_versions.return_value = []
    fake_uow.version_repository.get_most_important_version.return_value = None

    result = await status_service.check_latest_version(
        generic_latest_version.number - 1
    )

    assert result.answer.updateLogs == generic_latest_version.logs


@pytest.mark.asyncio
async def test_check_latest_version_collect_mini_logs(
    fake_uow,
    uow_factory,
    status_service,
    latest_version,
    generic_latest_version,
    mini_versions
):
    fake_uow.version_repository.get_latest_version.return_value = latest_version
    fake_uow.version_repository.get_latest_generic_version.return_value = generic_latest_version
    fake_uow.version_repository.get_latest_mini_versions.return_value = mini_versions
    fake_uow.version_repository.get_most_important_version.return_value = None

    result = await status_service.check_latest_version(
        generic_latest_version.number
    )

    expected_logs = "\n\n".join(
        version.logs
        for version in mini_versions
        if version.number > generic_latest_version.number
    )

    assert result.answer.updateLogs == expected_logs


@pytest.mark.asyncio
async def test_check_latest_version_adds_statistic(
    fake_uow,
    status_service,
    latest_version,
    generic_latest_version,
):
    fake_uow.version_repository.get_latest_version.return_value = latest_version
    fake_uow.version_repository.get_latest_generic_version.return_value = generic_latest_version
    fake_uow.version_repository.get_latest_mini_versions.return_value = []
    fake_uow.version_repository.get_most_important_version.return_value = None

    await status_service.check_latest_version(version_number=100)

    fake_uow.statistic_repository.add_statistic.assert_awaited_once_with(
        None,
        StatName.checkVersion
    )


@pytest.mark.asyncio
async def test_check_latest_version_without_latest(
    fake_uow,
    uow_factory,
    status_service
):
    fake_uow.version_repository.get_latest_version.return_value = None

    with pytest.raises(
        AssertionError,
        match="get_latest_version returned None"
    ):
        await status_service.check_latest_version(1)


@pytest.mark.asyncio
async def test_check_info_notifications(
    fake_uow,
    status_service,
    information,
    mock_status_check_session
):
    fake_uow.information_repository.get_informations.return_value = [
        information
    ]

    result = await status_service.check_info_notifications(
        "session_1"
    )

    assert len(result.answer.messages) == 1
    assert result.answer.messages[0].title == "Title"

    fake_uow.information_repository.delete_informations.assert_awaited_once()


@pytest.mark.asyncio
async def test_check_info_notifications_skip_review_if_review_exists(
    fake_session,
    fake_uow,
    status_service,
    review,
    review_information,
    mock_status_check_session
):
    fake_uow.information_repository.get_informations.return_value = [
        review_information
    ]

    fake_uow.review_repository.get_review.return_value = review

    response = await status_service.check_info_notifications(
        fake_session.session_id
    )

    assert response.answer.messages == []

    fake_uow.review_repository.get_review.assert_awaited_once_with(
        fake_session.parent_id,
        only_is_open=False
    )

    fake_uow.information_repository.create_information.assert_not_awaited()


@pytest.mark.asyncio
async def test_check_info_notifications_repeat_review_if_review_not_exists(
    status_service,
    fake_uow,
    fake_session,
    review_information,
    mock_status_check_session
):
    fake_uow.information_repository.get_informations.return_value = [
        review_information
    ]

    fake_uow.review_repository.get_review.return_value = None

    response = await status_service.check_info_notifications(
        fake_session.session_id
    )

    assert len(response.answer.messages) == 1
    assert response.answer.messages[0].title == review_information.title
    assert response.answer.messages[0].text == review_information.text

    fake_uow.review_repository.get_review.assert_awaited_once_with(
        fake_session.parent_id,
        only_is_open=False
    )

    fake_uow.information_repository.create_information.assert_awaited_once()


@pytest.mark.asyncio
async def test_check_info_notifications_skip_marks_notification_if_enabled(
    status_service,
    fake_uow,
    fake_session,
    marks_notification_information,
    marks_notification,
    mock_status_check_session
):
    fake_uow.information_repository.get_informations.return_value = [
        marks_notification_information
    ]

    fake_uow.marks_notification_repository.get_status.return_value = (
        marks_notification
    )

    response = await status_service.check_info_notifications(
        fake_session.session_id
    )

    assert response.answer.messages == []

    fake_uow.marks_notification_repository.get_status.assert_awaited_once_with(
        fake_session.session_id,
        fake_session.active_child_id
    )


@pytest.mark.asyncio
async def test_check_info_notifications_return_marks_notification_if_disabled(
    status_service,
    fake_uow,
    fake_session,
    marks_notification_information,
    mock_status_check_session
):
    fake_uow.information_repository.get_informations.return_value = [
        marks_notification_information
    ]

    fake_uow.marks_notification_repository.get_status.return_value = None

    response = await status_service.check_info_notifications(
        fake_session.session_id
    )

    assert len(response.answer.messages) == 1
    assert (
            response.answer.messages[0].title
            == marks_notification_information.title
    )
    assert (
            response.answer.messages[0].text
            == marks_notification_information.text
    )

    fake_uow.marks_notification_repository.get_status.assert_awaited_once_with(
        fake_session.session_id,
        fake_session.active_child_id
    )


@pytest.mark.asyncio
async def test_check_info_notifications_adds_statistic(
    fake_uow,
    fake_session,
    status_service,
    mock_status_check_session
):
    fake_uow.information_repository.get_informations.return_value = []

    await status_service.check_info_notifications(fake_session.session_id)

    fake_uow.statistic_repository.add_statistic.assert_awaited_once_with(
        fake_session.parent_id,
        StatName.checkInfoNotifications
    )
