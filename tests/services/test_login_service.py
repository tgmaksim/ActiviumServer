import pytest

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

from src.services.html_response import HtmlResponse
from src.utils.referral_token import encode_referral_token
from src.repositories.statistic_repository import StatName
from src.support.services.login_service import LoginService


@pytest.fixture
def login_service(uow_factory):
    return LoginService(
        uow_factory=uow_factory,
        httpx_client=AsyncMock()
    )


@pytest.fixture
def student_dnevnik_data():
    return {
        "me": {
            "person_id": 100001,
            "school_id": 1,
            "group_id": 2,
            "timezone": 10800
        }
    }


@pytest.fixture
def parent_dnevnik_data():
    return {
        "me": None,
        "parent_id": 500001,
        "children": [
            {
                "person_id": 200001,
                "school_id": 1,
                "group_id": 2,
                "timezone": 10800
            },
            {
                "person_id": 200002,
                "school_id": 1,
                "group_id": 3,
                "timezone": 10800
            }
        ]
    }


@pytest.fixture
def login_url():
    return "https://login.dnevnik.ru/auth"


@pytest.fixture
def mock_login_dnr(mock_dnr):
    with patch(
        "src.support.services.login_service.AioDnevnikruApi",
        return_value=mock_dnr
    ):
        yield mock_dnr


@pytest.fixture
def mock_create_session(login_service):
    with patch.object(
        login_service,
        "_create_session",
        new=AsyncMock(return_value="created_session")
    ) as mock:
        yield mock


@pytest.fixture
def mock_create_new_session(login_service):
    with patch.object(
        login_service,
        "_create_session",
        new=AsyncMock(return_value="new_session")
    ) as mock:
        yield mock


@pytest.fixture
def mock_build_login_url(login_url):
    with patch(
        "src.support.services.login_service.AioDnevnikruApi.build_login_url",
        return_value=login_url
    ) as mock:
        yield mock


@pytest.fixture
def mock_auth_session(login_service):
    with patch.object(
        login_service,
        "_auth_session",
        new=AsyncMock()
    ) as mock:
        yield mock


@pytest.fixture
def mock_auth_school_admin(login_service):
    with patch.object(
        login_service,
        "_auth_school_admin",
        new=AsyncMock()
    ) as mock:
        yield mock


@pytest.fixture
def mock_dnevnik_auth(login_service, student_dnevnik_data):
    with patch.object(
        login_service,
        "_dnevnik_auth",
        new=AsyncMock(
            return_value=(student_dnevnik_data, "Parent")
        )
    ) as mock:
        yield mock


@pytest.fixture
def mock_school_admin_dnevnik_auth(login_service, student_dnevnik_data):
    dnevnik_result = (
        "Admin",
        100001,
        200001,
        10800
    )

    with patch.object(
        login_service,
        "_school_admin_dnevnik_auth",
        new=AsyncMock(return_value=dnevnik_result)
    ) as mock:
        yield mock


@pytest.mark.asyncio
async def test_login_create_new_session(
    fake_uow,
    login_service,
    login_url,
    mock_create_new_session,
    mock_build_login_url
):
    fake_uow.session_repository.get_session.return_value = None

    result = await login_service.login(
        None,
        "firebase_token"
    )

    mock_create_new_session.assert_awaited_once()

    fake_uow.session_repository.update_firebase.assert_awaited_once_with(
        "new_session",
        "firebase_token"
    )

    assert result.answer.sessionId == "new_session"
    assert result.answer.loginUrl == login_url


@pytest.mark.asyncio
async def test_login_use_existing_session(
    fake_uow,
    login_service,
    login_url,
    fake_session,
    mock_create_session,
    mock_build_login_url,
):
    fake_uow.session_repository.get_session.return_value = fake_session

    result = await login_service.login(
        fake_session.session_id,
        "firebase_token"
    )

    mock_create_session.assert_not_awaited()

    fake_uow.session_repository.update_firebase.assert_awaited_once_with(
        fake_session.session_id,
        "firebase_token"
    )

    assert result.answer.sessionId == fake_session.session_id


@pytest.mark.asyncio
async def test_login_create_new_if_session_not_found(
    fake_uow,
    login_service,
    login_url,
    mock_create_session,
    mock_build_login_url
):
    fake_uow.session_repository.get_session.return_value = None

    result = await login_service.login(
        "old_session",
        "firebase_token"
    )

    mock_create_session.assert_awaited_once()

    assert result.answer.sessionId == "created_session"


@pytest.mark.asyncio
async def test_login_adds_statistic(
    fake_uow,
    login_service,
    login_url,
    mock_create_session,
    mock_build_login_url,
):
    await login_service.login(
        None,
        "firebase_token"
    )

    fake_uow.statistic_repository.add_statistic.assert_awaited_once_with(
        None,
        StatName.login
    )


@pytest.mark.asyncio
async def test_first_auth_session(
    login_service
):
    result = await login_service.firstAuthSession()

    assert isinstance(result, HtmlResponse)
    assert result.name == "auth_session.html"
    assert result.status_code == 200


@pytest.mark.asyncio
async def test_first_auth_school_admin(
    login_service
):
    response = await login_service.firstAuthSchoolAdmin()

    assert response.name == "auth_session.html"
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_second_auth_session_session_not_found(
    fake_uow,
    login_service
):
    fake_uow.session_repository.get_session.return_value = None

    result = await login_service.secondAuthSession(
        "token",
        "session_id",
        None
    )

    assert result.name == "error.html"
    assert result.status_code == 500

    fake_uow.log_repository.add_log.assert_awaited_once()


@pytest.mark.asyncio
async def test_second_auth_session_dnevnik_auth_failed(
    fake_uow,
    login_service,
    fake_session
):
    fake_uow.session_repository.get_session.return_value = fake_session

    with patch.object(
        login_service,
        "_dnevnik_auth",
        side_effect=RuntimeError("error")
    ):
        result = await login_service.secondAuthSession(
            "token",
            fake_session.session_id,
            None
        )

    assert result.name == "error.html"
    assert result.status_code == 500

    fake_uow.log_repository.add_log.assert_awaited_once()


@pytest.mark.asyncio
async def test_second_auth_session_teacher_forbidden(
    fake_uow,
    login_service,
    fake_session
):
    fake_uow.session_repository.get_session.return_value = fake_session

    with patch.object(
        login_service,
        "_dnevnik_auth",
        new=AsyncMock(return_value=("teacher", "Teacher"))
    ):
        result = await login_service.secondAuthSession(
            "token",
            fake_session.session_id,
            None
        )

    assert result.name == "auth_session_error.html"
    assert result.status_code == 403


@pytest.mark.asyncio
async def test_second_auth_session_success_without_referral(
    fake_uow,
    login_service,
    fake_session,
    student_dnevnik_data,
    mock_auth_session,
    mock_dnevnik_auth
):
    fake_uow.session_repository.get_session.return_value = fake_session

    result = await login_service.secondAuthSession(
        "token",
        fake_session.session_id,
        None
    )

    mock_auth_session.assert_awaited_once_with(
        fake_uow,
        fake_session.session_id,
        "token",
        student_dnevnik_data,
        "Parent",
        None
    )

    assert result.name == "auth_session_success.html"

    assert result.cookies[0]["key"] == "session_id"
    assert result.cookies[0]["value"] == fake_session.session_id


@pytest.mark.asyncio
async def test_second_auth_session_valid_referral(
    fake_uow,
    login_service,
    fake_session,
    fake_parent,
    student_dnevnik_data,
    mock_dnevnik_auth,
    mock_auth_session
):
    fake_uow.session_repository.get_session.return_value = fake_session
    fake_uow.parent_repository.get_parent.return_value = fake_parent

    referral_token = encode_referral_token(fake_parent.parent_id)

    await login_service.secondAuthSession(
        "token",
        fake_session.session_id,
        referral_token
    )

    mock_auth_session.assert_awaited_once_with(
        fake_uow,
        fake_session.session_id,
        "token",
        student_dnevnik_data,
        "Parent",
        fake_parent.parent_id
    )


@pytest.mark.asyncio
async def test_second_auth_session_invalid_referral_token(
    fake_uow,
    login_service,
    fake_session,
    student_dnevnik_data,
    mock_dnevnik_auth,
    mock_auth_session
):
    fake_uow.session_repository.get_session.return_value = fake_session

    response = await login_service.secondAuthSession(
        "token",
        fake_session.session_id,
        "invalid"
    )

    assert response.name == "auth_session_success.html"

    mock_auth_session.assert_awaited_once()

    assert mock_auth_session.await_args.args[5] is None


@pytest.mark.asyncio
async def test_second_auth_session_referral_parent_not_found(
    fake_uow,
    login_service,
    fake_session,
    student_dnevnik_data,
    mock_dnevnik_auth,
    mock_auth_session
):
    fake_uow.session_repository.get_session.return_value = fake_session
    fake_uow.parent_repository.get_parent.return_value = None

    response = await login_service.secondAuthSession(
        "token",
        fake_session.session_id,
        hex(100001)[2:]
    )

    assert response.name == "auth_session_success.html"

    mock_auth_session.assert_awaited_once()

    assert mock_auth_session.await_args.args[5] is None


@pytest.mark.asyncio
async def test_second_auth_session_session_not_found(
    login_service,
    fake_uow
):
    fake_uow.session_repository.get_session.return_value = None

    response = await login_service.secondAuthSession(
        dnevnik_token="token",
        session_id="session_1",
        referral_token=None
    )

    assert response.name == "error.html"
    assert response.status_code == 500

    fake_uow.log_repository.add_log.assert_awaited_once()


@pytest.mark.asyncio
async def test_auth_session_register_student(
    fake_uow,
    login_service,
    student_dnevnik_data
):
    fake_uow.parent_repository.get_parent.return_value = None

    await login_service._auth_session(
        fake_uow,
        "session",
        "token",
        student_dnevnik_data,
        "User",
        None
    )

    fake_uow.child_repository.create_child.assert_awaited_once()
    fake_uow.parent_repository.create_parent.assert_awaited_once()
    fake_uow.session_repository.auth_session.assert_awaited_once()

    assert fake_uow.statistic_repository.add_statistic.await_count == 2


@pytest.mark.asyncio
async def test_auth_session_existing_student(
    fake_uow,
    login_service,
    student_dnevnik_data
):
    child = SimpleNamespace(
        school_id=1,
        group_id=2,
        timezone=10800
    )

    fake_uow.parent_repository.get_parent.return_value = object()
    fake_uow.child_repository.get_child.return_value = child

    await login_service._auth_session(
        fake_uow,
        "session",
        "token",
        student_dnevnik_data,
        "User",
        None
    )

    fake_uow.child_repository.update_child.assert_not_awaited()


@pytest.mark.asyncio
async def test_auth_session_update_student(
    fake_uow,
    login_service,
    student_dnevnik_data
):
    child = SimpleNamespace(
        school_id=999,
        group_id=999,
        timezone=999
    )

    fake_uow.parent_repository.get_parent.return_value = object()
    fake_uow.child_repository.get_child.return_value = child

    await login_service._auth_session(
        fake_uow,
        "session",
        "token",
        student_dnevnik_data,
        "User",
        None
    )

    fake_uow.child_repository.update_child.assert_awaited_once()


@pytest.mark.asyncio
async def test_auth_session_register_parent(
    fake_uow,
    login_service,
    parent_dnevnik_data
):
    fake_uow.parent_repository.get_parent.return_value = None

    await login_service._auth_session(
        fake_uow,
        "session",
        "token",
        parent_dnevnik_data,
        "Parent",
        None
    )

    assert fake_uow.child_repository.create_child.await_count == 2

    fake_uow.parent_repository.create_parent.assert_awaited_once()


@pytest.mark.asyncio
async def test_auth_session_create_referral(
    fake_uow,
    login_service,
    student_dnevnik_data
):
    fake_uow.parent_repository.get_parent.return_value = None

    await login_service._auth_session(
        fake_uow,
        "session",
        "token",
        student_dnevnik_data,
        "User",
        555
    )

    fake_uow.referral_repository.link_referral.assert_awaited_once()


@pytest.mark.asyncio
async def test_auth_session_skip_self_referral(
    fake_uow,
    login_service,
    student_dnevnik_data
):
    fake_uow.parent_repository.get_parent.return_value = None

    await login_service._auth_session(
        fake_uow,
        "session",
        "token",
        student_dnevnik_data,
        "User",
        100001
    )

    fake_uow.referral_repository.link_referral.assert_not_awaited()


@pytest.mark.asyncio
async def test_check_session_not_exists(
    login_service,
    fake_uow
):
    fake_uow.session_repository.get_session.return_value = None

    response = await login_service.checkSession("session")

    assert response.answer.exists is False
    assert response.answer.auth is False


@pytest.mark.asyncio
async def test_check_session_authorized(
    login_service,
    fake_uow,
    fake_session
):
    fake_uow.session_repository.get_session.return_value = fake_session
    fake_uow.session_repository.check_session_auth.return_value = True

    response = await login_service.checkSession("session")

    assert response.answer.exists is True
    assert response.answer.auth is True


@pytest.mark.asyncio
async def test_check_session_adds_statistic(
    login_service,
    fake_uow,
    fake_session
):
    fake_uow.session_repository.get_session.return_value = fake_session
    fake_uow.session_repository.check_session_auth.return_value = True

    await login_service.checkSession("session")

    fake_uow.statistic_repository.add_statistic.assert_awaited_once_with(
        fake_session.parent_id,
        StatName.checkSession
    )


@pytest.mark.asyncio
async def test_dnevnik_auth_student(
    login_service,
    mock_dnr,
    mock_login_dnr
):
    mock_dnr.get_context.return_value = {
        "personId": 100001,
        "shortName": "Student",
        "roles": ["EduStudent"],
        "schoolIds": [10],
        "schools": [
            {
                "id": 10,
                "type": "Regular",
                "groupIds": [20]
            }
        ],
        "eduGroups": [
            {
                "id": 20,
                "type": "Group"
            }
        ]
    }

    mock_dnr.get_info.return_value = {
        "timezone": "03:00"
    }

    result, parent_name = await login_service._dnevnik_auth("token")

    assert parent_name == "Student"

    assert result["me"] == {
        "person_id": 100001,
        "school_id": 10,
        "group_id": 20,
        "timezone": 10800
    }


@pytest.mark.asyncio
async def test_dnevnik_auth_parent(
    login_service,
    mock_dnr,
    mock_login_dnr
):
    mock_dnr.get_context.return_value = {
        "personId": 500001,
        "shortName": "Parent",
        "roles": ["EduParent"],
        "children": [
            {
                "personId": 200001,
                "schoolIds": [10],
                "groupIds": [20]
            }
        ],
        "schools": [
            {
                "id": 10,
                "type": "Regular"
            }
        ],
        "eduGroups": [
            {
                "id": 20,
                "type": "Group"
            }
        ]
    }

    mock_dnr.get_children.return_value = [
        {
            "userId": 777
        }
    ]

    mock_dnr.get_user_info.return_value = {
        "personId": 200001,
        "timezone": "03:00"
    }

    result, parent_name = await login_service._dnevnik_auth("token")

    assert parent_name == "Parent"

    assert result["parent_id"] == 500001
    assert len(result["children"]) == 1

    assert result["children"][0]['person_id'] == 200001
    assert result["children"][0]['timezone'] == 10800


@pytest.mark.asyncio
async def test_dnevnik_auth_teacher(
    login_service,
    mock_dnr,
    mock_login_dnr
):
    mock_dnr.get_context.return_value = {
        "personId": 1,
        "shortName": "Teacher",
        "roles": ["EduStaff"],
        "schools": []
    }

    result, parent_name = await login_service._dnevnik_auth("token")

    assert result == "teacher"
    assert parent_name == "Teacher"


@pytest.mark.asyncio
async def test_dnevnik_auth_school_admin(
    login_service,
    mock_dnr,
    mock_login_dnr
):
    mock_dnr.get_context.return_value = {
        "personId": 1,
        "shortName": "Admin",
        "roles": ["EduSchoolAdministrator"],
        "schools": []
    }

    result, _ = await login_service._dnevnik_auth("token")

    assert result == "teacher"


@pytest.mark.asyncio
async def test_dnevnik_auth_unknown_role(
    login_service,
    mock_dnr,
    mock_login_dnr
):
    mock_dnr.get_context.return_value = {
        "personId": 1,
        "shortName": "User",
        "roles": [],
        "schools": []
    }

    result, _ = await login_service._dnevnik_auth("token")

    assert result is None


@pytest.mark.asyncio
async def test_create_review_information(
    fake_uow,
    login_service
):
    await login_service.create_review_information(
        fake_uow.information_repository,
        100001
    )

    fake_uow.information_repository.create_information.assert_awaited_once()

    args = (
        fake_uow
        .information_repository
        .create_information
        .await_args
        .args
    )

    assert args[0] == 100001
    assert args[1] == "review"


@pytest.mark.asyncio
async def test_create_marks_notifications_information(
    fake_uow,
    login_service
):
    await login_service.create_marks_notifications_information(
        fake_uow.information_repository,
        100001
    )

    fake_uow.information_repository.create_information.assert_awaited_once()

    args = (
        fake_uow
        .information_repository
        .create_information
        .await_args
        .args
    )

    assert args[0] == 100001
    assert args[1] == "marks_notifications"


@pytest.mark.asyncio
async def test_auth_session_existing_parent_without_child_changes(
    fake_uow,
    login_service,
    parent_dnevnik_data
):
    fake_uow.parent_repository.get_parent.return_value = object()

    fake_uow.child_repository.get_child.side_effect = [
        SimpleNamespace(
            school_id=1,
            group_id=2,
            timezone=10800
        ),
        SimpleNamespace(
            school_id=1,
            group_id=3,
            timezone=10800
        )
    ]

    await login_service._auth_session(
        fake_uow,
        "session",
        "token",
        parent_dnevnik_data,
        "Parent",
        None
    )

    fake_uow.child_repository.create_child.assert_not_awaited()


@pytest.mark.asyncio
async def test_auth_session_existing_parent_with_child_changes(
    fake_uow,
    login_service,
    parent_dnevnik_data
):
    fake_uow.parent_repository.get_parent.return_value = object()

    fake_uow.child_repository.get_child.side_effect = [
        SimpleNamespace(
            school_id=999,
            group_id=999,
            timezone=999
        ),
        SimpleNamespace(
            school_id=1,
            group_id=3,
            timezone=10800
        )
    ]

    await login_service._auth_session(
        fake_uow,
        "session",
        "token",
        parent_dnevnik_data,
        "Parent",
        None
    )

    assert fake_uow.child_repository.create_child.await_count == 1


@pytest.mark.asyncio
async def test_second_auth_school_admin_dnevnik_error(
    login_service,
    fake_uow
):
    with patch.object(
        login_service,
        "_school_admin_dnevnik_auth",
        AsyncMock(side_effect=RuntimeError())
    ):
        response = await login_service.secondAuthSchoolAdmin(
            dnevnik_token="token",
            user_id=123
        )

    assert response.name == "error.html"
    assert response.status_code == 500

    fake_uow.log_repository.add_log.assert_awaited_once()


@pytest.mark.asyncio
async def test_second_auth_school_admin_not_admin(
    login_service,
    fake_uow
):
    with patch.object(
        login_service,
        "_school_admin_dnevnik_auth",
        AsyncMock(return_value="no_admin")
    ):
        response = await login_service.secondAuthSchoolAdmin(
            dnevnik_token="token",
            user_id=123
        )

    assert response.name == "auth_session_error.html"
    assert response.status_code == 403

    fake_uow.log_repository.add_log.assert_awaited_once()


@pytest.mark.asyncio
async def test_second_auth_school_admin_success(
    login_service,
    mock_school_admin_dnevnik_auth,
    mock_auth_school_admin
):
    response = await login_service.secondAuthSchoolAdmin(
        dnevnik_token="token",
        user_id=123
    )

    assert response.name == "auth_school_admin_success.html"

    mock_auth_school_admin.assert_awaited_once()


@pytest.mark.asyncio
async def test_second_auth_school_admin_calls_auth_with_correct_args(
    login_service,
    mock_school_admin_dnevnik_auth,
    mock_auth_school_admin
):
    await login_service.secondAuthSchoolAdmin(
        dnevnik_token="token",
        user_id=123
    )

    args = mock_auth_school_admin.await_args.args

    assert args[1:] == (
        123,
        "Admin",
        100001,
        200001,
        10800,
        "token"
    )


@pytest.mark.asyncio
async def test_school_admin_dnevnik_auth_staff(
    login_service,
    mock_dnr,
    mock_login_dnr
):
    mock_dnr.get_info.return_value = {
        "timezone": "03:00"
    }

    mock_dnr.get_context.return_value = {
        "personId": 100001,
        "shortName": "Admin",
        "roles": ["EduStaff"],
        "schoolIds": [10],
        "schools": [
            {
                "id": 10,
                "type": "Regular"
            }
        ]
    }

    result = await login_service._school_admin_dnevnik_auth(
        "token"
    )

    assert result == (
        "Admin",
        100001,
        10,
        10800
    )


@pytest.mark.asyncio
async def test_school_admin_dnevnik_auth_school_administrator(
    login_service,
    mock_dnr,
    mock_login_dnr
):
    mock_dnr.get_info.return_value = {
        "timezone": "03:00"
    }

    mock_dnr.get_context.return_value = {
        "personId": 100001,
        "shortName": "Admin",
        "roles": ["EduSchoolAdministrator"],
        "schoolIds": [10],
        "schools": [
            {
                "id": 10,
                "type": "Regular"
            }
        ]
    }

    result = await login_service._school_admin_dnevnik_auth(
        "token"
    )

    assert result == (
        "Admin",
        100001,
        10,
        10800
    )


@pytest.mark.asyncio
async def test_school_admin_dnevnik_auth_no_admin(
    login_service,
    mock_dnr,
    mock_login_dnr
):
    mock_dnr.get_info.return_value = {
        "timezone": "03:00"
    }

    mock_dnr.get_context.return_value = {
        "personId": 100001,
        "shortName": "User",
        "roles": ["EduParent"],
        "schoolIds": [10],
        "schools": []
    }

    result = await login_service._school_admin_dnevnik_auth(
        "token"
    )

    assert result == "no_admin"


@pytest.mark.asyncio
async def test_auth_school_admin_registration(
    fake_uow,
    login_service
):
    fake_uow.school_admin_repository.get_admin.return_value = None

    await login_service._auth_school_admin(
        fake_uow,
        user_id=1,
        name="Admin",
        person_id=100,
        school_id=200,
        timezone=10800,
        dnevnik_token="token"
    )

    fake_uow.school_admin_repository.create_admin.assert_awaited_once()

    fake_uow.statistic_repository.add_statistic.assert_awaited_once_with(
        1,
        StatName.registrationSchoolAdmin
    )


@pytest.mark.asyncio
async def test_auth_school_admin_authorization(
    fake_uow,
    login_service
):
    fake_uow.school_admin_repository.get_admin.return_value = object()

    await login_service._auth_school_admin(
        fake_uow,
        user_id=1,
        name="Admin",
        person_id=100,
        school_id=200,
        timezone=10800,
        dnevnik_token="token"
    )

    fake_uow.school_admin_repository.create_admin.assert_awaited_once()

    fake_uow.statistic_repository.add_statistic.assert_awaited_once_with(
        1,
        StatName.authorizationSchoolAdmin
    )


@pytest.mark.asyncio
async def test_auth_school_admin_create_admin_arguments(
    fake_uow,
    login_service
):
    fake_uow.school_admin_repository.get_admin.return_value = object()

    await login_service._auth_school_admin(
        fake_uow,
        user_id=1,
        name="Admin",
        person_id=100,
        school_id=200,
        timezone=10800,
        dnevnik_token="token"
    )

    fake_uow.school_admin_repository.create_admin.assert_awaited_once_with(
        1,
        "Admin",
        None,
        100,
        200,
        10800,
        "token"
    )
