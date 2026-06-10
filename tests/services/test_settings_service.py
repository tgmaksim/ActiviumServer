import pytest

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from src.dependencies.referral_token import encode_referral_token
from src.repositories.statistic_repository import StatName
from src.support.services.settings_service import SettingsService


@pytest.fixture
def settings_service(uow_factory):
    return SettingsService(
        uow_factory=uow_factory,
        httpx_client=AsyncMock()
    )


@pytest.fixture
def mock_settings_check_session(fake_session_with_parent):
    with patch(
        "src.support.services.settings_service.check_session",
        new=AsyncMock(return_value=fake_session_with_parent)
    ) as mock:
        yield mock


@pytest.fixture
def mock_settings_dnr(mock_dnr):
    with patch(
        "src.support.services.settings_service.AioDnevnikruApi",
        return_value=mock_dnr
    ):
        yield mock_dnr


@pytest.fixture
def children():
    return [
        {
            "id": 200001,
            "shortName": "Иван"
        },
        {
            "id": 200002,
            "shortName": "Петр"
        }
    ]


@pytest.fixture
def student_info():
    return {
        "personId": 200001,
        "shortName": "Максим"
    }


@pytest.fixture
def child_context():
    return {
        "schools": [
            {
                "id": 100,
                "type": "Regular",
                "groupIds": [300]
            }
        ],
        "eduGroups": [
            {
                "id": 300,
                "type": "Group"
            }
        ],
        "children": [
            {
                "personId": 200002,
                "schoolIds": [100]
            }
        ]
    }


@pytest.mark.asyncio
async def test_get_children_parent(
    settings_service,
    fake_uow,
    fake_session_with_parent,
    children,
    student_info,
    mock_settings_check_session,
    mock_settings_dnr
):
    mock_settings_dnr.get_children.return_value = children
    mock_settings_dnr.get_info.return_value = student_info

    response = await settings_service.getChildren(
        fake_session_with_parent.session_id
    )

    assert len(response.answer.children) == 2
    assert response.answer.children[0].childId == 200001
    assert response.answer.children[0].name == "Иван"

    assert (
        response.answer.activeChildId
        == fake_session_with_parent.active_child_id
    )

    fake_uow.statistic_repository.add_statistic.assert_awaited_once_with(
        fake_session_with_parent.parent.parent_id,
        StatName.getChildren
    )


@pytest.mark.asyncio
async def test_get_children_student_profile(
    settings_service,
    fake_session_with_parent,
    mock_settings_check_session,
    mock_settings_dnr
):
    mock_settings_dnr.get_children.return_value = []
    mock_settings_dnr.get_info.return_value = {
        "personId": 123456,
        "shortName": "Максим"
    }

    response = await settings_service.getChildren(
        fake_session_with_parent.session_id
    )

    assert len(response.answer.children) == 1
    assert response.answer.children[0].childId == 123456
    assert response.answer.children[0].name == "Максим"


@pytest.mark.asyncio
async def test_set_active_child_success(
    settings_service,
    fake_uow,
    fake_session_with_parent,
    children,
    student_info,
    fake_child,
    mock_settings_check_session,
    mock_settings_dnr
):
    mock_settings_dnr.get_children.return_value = children
    mock_settings_dnr.get_info.return_value = student_info

    fake_uow.child_repository.get_child.return_value = fake_child

    response = await settings_service.setActiveChild(
        fake_session_with_parent.session_id,
        200002
    )

    fake_uow.session_repository.set_active_child.assert_awaited_once_with(
        fake_session_with_parent.session_id,
        200002
    )

    fake_uow.statistic_repository.add_statistic.assert_awaited_once_with(
        fake_session_with_parent.parent.parent_id,
        StatName.setActiveChild
    )

    assert response.answer.activeChildId == 200002


@pytest.mark.asyncio
async def test_set_active_child_self_student(
    settings_service,
    fake_session_with_parent,
    mock_settings_check_session,
    mock_settings_dnr
):
    mock_settings_dnr.get_children.return_value = []

    mock_settings_dnr.get_info.return_value = {
        "personId": fake_session_with_parent.parent.parent_id,
        "shortName": "Максим"
    }

    response = await settings_service.setActiveChild(
        fake_session_with_parent.session_id,
        fake_session_with_parent.parent.parent_id
    )

    assert len(response.answer.children) == 1
    assert (
        response.answer.activeChildId
        == fake_session_with_parent.parent.parent_id
    )


@pytest.mark.asyncio
async def test_set_active_child_not_found(
    settings_service,
    fake_uow,
    fake_session_with_parent,
    mock_settings_check_session,
    mock_settings_dnr
):
    mock_settings_dnr.get_children.return_value = [
        {"id": 1, "shortName": "A"}
    ]

    mock_settings_dnr.get_info.return_value = {
        "personId": 1,
        "shortName": "A"
    }

    response = await settings_service.setActiveChild(
        fake_session_with_parent.session_id,
        999
    )

    assert response.status is False
    assert response.error.type == "ValueError"

    fake_uow.log_repository.add_log.assert_awaited_once()


@pytest.mark.asyncio
async def test_set_active_child_create_child_if_not_exists(
    settings_service,
    fake_uow,
    fake_session_with_parent,
    children,
    child_context,
    mock_settings_check_session,
    mock_settings_dnr
):
    fake_uow.child_repository.get_child.return_value = None

    mock_settings_dnr.get_children.return_value = [
        {
            "id": 200002,
            "userId": 500,
            "shortName": "Петр"
        }
    ]

    mock_settings_dnr.get_info.return_value = {
        "personId": 1,
        "shortName": "Parent"
    }

    mock_settings_dnr.get_context.return_value = child_context

    mock_settings_dnr.get_user_info.return_value = {
        "timezone": "03:00"
    }

    await settings_service.setActiveChild(
        fake_session_with_parent.session_id,
        200002
    )

    fake_uow.child_repository.create_child.assert_awaited_once_with(
        child_id=200002,
        school_id=100,
        group_id=300,
        timezone=10800
    )


@pytest.mark.asyncio
async def test_get_status_marks_notifications_enabled(
    settings_service,
    fake_uow,
    fake_session,
    fake_parent,
    mock_settings_check_session
):
    fake_session.parent = fake_parent

    fake_uow.marks_notification_repository.get_status.return_value = object()

    result = await settings_service.getStatusMarksNotifications(
        fake_session.session_id,
        fake_session.active_child_id
    )

    assert result.answer.status is True

    fake_uow.marks_notification_repository.get_status.assert_awaited_once_with(
        fake_session.session_id,
        fake_session.active_child_id
    )


@pytest.mark.asyncio
async def test_get_status_marks_notifications_disabled(
    settings_service,
    fake_uow,
    fake_session,
    fake_parent,
    mock_settings_check_session
):
    fake_session.parent = fake_parent

    fake_uow.marks_notification_repository.get_status.return_value = None

    result = await settings_service.getStatusMarksNotifications(
        fake_session.session_id,
        fake_session.active_child_id
    )

    assert result.answer.status is False


@pytest.mark.asyncio
async def test_get_status_marks_notifications_use_active_child(
    settings_service,
    fake_uow,
    fake_session,
    fake_parent,
    mock_settings_check_session
):
    fake_session.parent = fake_parent

    await settings_service.getStatusMarksNotifications(
        fake_session.session_id,
        None
    )

    fake_uow.marks_notification_repository.get_status.assert_awaited_once_with(
        fake_session.session_id,
        fake_session.active_child_id
    )


@pytest.mark.asyncio
async def test_switch_marks_notifications_turn_off(
    settings_service,
    fake_uow,
    fake_session,
    fake_parent,
    mock_settings_check_session
):
    fake_session.parent = fake_parent

    await settings_service.switchMarksNotifications(
        fake_session.session_id,
        fake_session.active_child_id,
        False
    )

    fake_uow.marks_notification_repository.turn_off.assert_awaited_once_with(
        fake_session.session_id,
        fake_session.active_child_id
    )

    fake_uow.statistic_repository.add_statistic.assert_awaited_once_with(
        fake_parent.parent_id,
        StatName.turnOffMarksNotifications
    )


@pytest.mark.asyncio
async def test_switch_marks_notifications_turn_on_active_child(
    settings_service,
    fake_uow,
    fake_session,
    fake_parent,
    mock_settings_check_session
):
    fake_session.parent = fake_parent

    await settings_service.switchMarksNotifications(
        fake_session.session_id,
        fake_session.active_child_id,
        True
    )

    fake_uow.marks_notification_repository.turn_on.assert_awaited_once_with(
        fake_session.session_id,
        fake_session.active_child_id
    )

    fake_uow.statistic_repository.add_statistic.assert_awaited_once_with(
        fake_parent.parent_id,
        StatName.turnOnMarksNotifications
    )


@pytest.mark.asyncio
async def test_switch_marks_notifications_turn_on_other_child(
    settings_service,
    fake_uow,
    fake_session,
    fake_parent,
    mock_settings_check_session,
    mock_settings_dnr
):
    fake_session.parent = fake_parent
    fake_session.dnevnik_token = "token"

    child_id = 200002

    mock_settings_dnr.get_children.return_value = [
        {"id": child_id}
    ]

    await settings_service.switchMarksNotifications(
        fake_session.session_id,
        child_id,
        True
    )

    fake_uow.marks_notification_repository.turn_on.assert_awaited_once_with(
        fake_session.session_id,
        child_id
    )


@pytest.mark.asyncio
async def test_switch_marks_notifications_child_not_found(
    settings_service,
    fake_uow,
    fake_session,
    fake_parent,
    mock_settings_check_session,
    mock_settings_dnr
):
    fake_session.parent = fake_parent
    fake_session.dnevnik_token = "token"

    mock_settings_dnr.get_children.return_value = []

    result = await settings_service.switchMarksNotifications(
        fake_session.session_id,
        999999,
        True
    )

    assert result.status is False
    assert result.error.errorMessage == "Ребенок не найден"

    fake_uow.log_repository.add_log.assert_awaited_once()


@pytest.mark.asyncio
async def test_update_firebase(
    settings_service,
    fake_uow,
    fake_session,
    mock_settings_check_session
):
    token = "firebase_token"

    await settings_service.update_firebase(
        fake_session.session_id,
        token
    )

    fake_uow.session_repository.update_firebase.assert_awaited_once_with(
        fake_session.session_id,
        token
    )

    fake_uow.statistic_repository.add_statistic.assert_awaited_once_with(
        fake_session.parent_id,
        StatName.updateFirebase
    )


@pytest.mark.asyncio
async def test_get_status_ea_notifications_enabled(
    settings_service,
    fake_uow,
    fake_session,
    mock_settings_check_session
):
    fake_uow.ea_notification_repository.get_status.return_value = object()

    result = await settings_service.getStatusEANotifications(
        fake_session.session_id,
        fake_session.active_child_id
    )

    assert result.answer.status is True


@pytest.mark.asyncio
async def test_get_status_ea_notifications_disabled(
    settings_service,
    fake_uow,
    fake_session,
    mock_settings_check_session
):
    fake_uow.ea_notification_repository.get_status.return_value = None

    result = await settings_service.getStatusEANotifications(
        fake_session.session_id,
        fake_session.active_child_id
    )

    assert result.answer.status is False


@pytest.mark.asyncio
async def test_get_status_ea_notifications_use_active_child(
    settings_service,
    fake_uow,
    fake_session,
    mock_settings_check_session
):
    await settings_service.getStatusEANotifications(
        fake_session.session_id,
        None
    )

    fake_uow.ea_notification_repository.get_status.assert_awaited_once_with(
        fake_session.session_id,
        fake_session.active_child_id
    )


@pytest.mark.asyncio
async def test_switch_ea_notifications_turn_off(
    settings_service,
    fake_uow,
    fake_session,
    fake_parent,
    mock_settings_check_session
):
    fake_session.parent = fake_parent

    await settings_service.switchEANotifications(
        fake_session.session_id,
        fake_session.active_child_id,
        False
    )

    fake_uow.ea_notification_repository.turn_off.assert_awaited_once_with(
        fake_session.session_id,
        fake_session.active_child_id
    )

    fake_uow.statistic_repository.add_statistic.assert_awaited_once_with(
        fake_parent.parent_id,
        StatName.turnOffEANotifications
    )


@pytest.mark.asyncio
async def test_switch_ea_notifications_turn_on(
    settings_service,
    fake_uow,
    fake_session,
    fake_parent,
    mock_settings_check_session
):
    fake_session.parent = fake_parent

    await settings_service.switchEANotifications(
        fake_session.session_id,
        fake_session.active_child_id,
        True
    )

    fake_uow.ea_notification_repository.turn_on.assert_awaited_once_with(
        fake_session.session_id,
        fake_session.active_child_id
    )

    fake_uow.statistic_repository.add_statistic.assert_awaited_once_with(
        fake_parent.parent_id,
        StatName.turnOnEANotifications
    )


@pytest.mark.asyncio
async def test_switch_ea_notifications_child_not_found(
    settings_service,
    fake_uow,
    fake_session,
    fake_parent,
    mock_settings_check_session,
    mock_settings_dnr
):
    fake_session.parent = fake_parent
    fake_session.dnevnik_token = "token"

    mock_settings_dnr.get_children.return_value = []

    result = await settings_service.switchEANotifications(
        fake_session.session_id,
        999999,
        True
    )

    assert result.status is False
    assert result.error.errorMessage == "Ребенок не найден"


@pytest.mark.asyncio
async def test_get_referral_params(
    settings_service,
    fake_uow,
    fake_session,
    fake_parent,
    mock_settings_check_session
):
    fake_session.parent = fake_parent

    fake_uow.referral_repository.get_me_referral.return_value = (
        SimpleNamespace(name="Ivan")
    )
    fake_uow.referral_repository.get_count_my_referrals.return_value = 5

    result = await settings_service.getReferralParams(
        fake_session.session_id
    )

    assert result.answer.meReferralName == "Ivan"
    assert result.answer.referralsCount == 5

    assert encode_referral_token(fake_parent.parent_id) in result.answer.referralUrl


@pytest.mark.asyncio
async def test_get_referral_params_without_referral(
    settings_service,
    fake_uow,
    fake_session,
    fake_parent,
    mock_settings_check_session
):
    fake_session.parent = fake_parent

    fake_uow.referral_repository.get_me_referral.return_value = None
    fake_uow.referral_repository.get_count_my_referrals.return_value = 0

    result = await settings_service.getReferralParams(
        fake_session.session_id
    )

    assert result.answer.meReferralName is None
    assert result.answer.referralsCount == 0
