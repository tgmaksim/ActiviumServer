import pytest

from sqlalchemy.exc import IntegrityError

from src.models import SchoolAdmin
from src.support.repositories.school_admin_repository import SchoolAdminRepository


@pytest.fixture
def school_admin_repository(session):
    return SchoolAdminRepository(session)


@pytest.fixture
async def school_admin(
    school_admin_repository: SchoolAdminRepository
):
    await school_admin_repository.create_admin(
        user_id=1,
        name="Main admin",
        parent_admin_id=None,
        person_id=100,
        school_id=500,
        timezone=0,
        dnevnik_token="token"
    )

    return await school_admin_repository.get_admin(1)


@pytest.fixture
async def child_school_admin(
    school_admin_repository: SchoolAdminRepository,
    school_admin
):
    await school_admin_repository.create_admin(
        user_id=2,
        name="Child admin",
        parent_admin_id=school_admin.user_id,
        person_id=None,
        school_id=None,
        timezone=None,
        dnevnik_token=None
    )

    return await school_admin_repository.get_admin(2)


@pytest.mark.asyncio
async def test_create_admin_with_unknown_parent_raises_error(
    school_admin_repository: SchoolAdminRepository
):
    with pytest.raises(IntegrityError):
        await school_admin_repository.create_admin(
            user_id=2,
            name="Admin",
            parent_admin_id=999,
            person_id=None,
            school_id=None,
            timezone=None,
            dnevnik_token=None
        )


@pytest.mark.asyncio
async def test_create_self_admin_raises_error(
    school_admin_repository: SchoolAdminRepository
):
    with pytest.raises(IntegrityError):
        await school_admin_repository.create_admin(
            user_id=1,
            name="Admin",
            parent_admin_id=1,
            person_id=None,
            school_id=None,
            timezone=None,
            dnevnik_token=None
        )


@pytest.mark.asyncio
async def test_create_main_admin_without_required_fields_raises_error(
    school_admin_repository
):
    with pytest.raises(IntegrityError):
        await school_admin_repository.create_admin(
            user_id=1,
            name="Admin",
            parent_admin_id=None,
            person_id=None,
            school_id=100,
            timezone=10800,
            dnevnik_token="token"
        )


@pytest.mark.asyncio
async def test_get_admin(
    school_admin_repository: SchoolAdminRepository,
    school_admin
):
    result = await school_admin_repository.get_admin(
        school_admin.user_id
    )

    assert result is not None

    assert result.user_id == school_admin.user_id
    assert result.name == school_admin.name


@pytest.mark.asyncio
async def test_get_unknown_admin_returns_none(
    school_admin_repository: SchoolAdminRepository
):
    result = await school_admin_repository.get_admin(
        999
    )

    assert result is None


@pytest.mark.asyncio
async def test_get_my_admins(
    school_admin_repository: SchoolAdminRepository,
    child_school_admin,
    school_admin
):
    result = await school_admin_repository.get_my_admins(
        school_admin.user_id
    )

    assert len(result) == 1

    assert result[0].user_id == child_school_admin.user_id


@pytest.mark.asyncio
async def test_get_my_admins_returns_empty(
    school_admin_repository: SchoolAdminRepository
):
    result = await school_admin_repository.get_my_admins(
        999
    )

    assert result == []


@pytest.mark.asyncio
async def test_add_my_admins(
    school_admin_repository: SchoolAdminRepository,
    school_admin
):
    result = await school_admin_repository.add_my_admins(
        school_admin.user_id,
        [
            (2, "Admin 1"),
            (3, "Admin 2")
        ]
    )

    assert len(result) == 2

    admins = await school_admin_repository.get_my_admins(
        school_admin.user_id
    )

    assert len(admins) == 2


@pytest.mark.asyncio
async def test_add_my_admins_ignores_duplicates(
    school_admin_repository: SchoolAdminRepository,
    school_admin
):
    await school_admin_repository.add_my_admins(
        school_admin.user_id,
        [
            (2, "Admin")
        ]
    )

    result = await school_admin_repository.add_my_admins(
        school_admin.user_id,
        [
            (2, "New name")
        ]
    )

    admins = await school_admin_repository.get_my_admins(
        school_admin.user_id
    )

    assert result == []
    assert len(admins) == 1

    assert admins[0].name == "Admin"


@pytest.mark.asyncio
async def test_add_my_admins_cuts_long_name(
    school_admin_repository: SchoolAdminRepository,
    school_admin
):
    long_name = "a" * 100

    await school_admin_repository.add_my_admins(
        school_admin.user_id,
        [
            (2, long_name)
        ]
    )

    admin = await school_admin_repository.get_admin(
        2
    )

    assert len(admin.name) == 64


@pytest.mark.asyncio
async def test_delete_my_admin(
    school_admin_repository: SchoolAdminRepository,
    child_school_admin,
    school_admin
):
    await school_admin_repository.delete_my_admin(
        school_admin.user_id,
        child_school_admin.user_id
    )

    result = await school_admin_repository.get_admin(
        child_school_admin.user_id
    )

    assert result is None


@pytest.mark.asyncio
async def test_delete_other_admin_does_nothing(
    school_admin_repository: SchoolAdminRepository,
    child_school_admin
):
    await school_admin_repository.delete_my_admin(
        999,
        child_school_admin.user_id
    )

    result = await school_admin_repository.get_admin(
        child_school_admin.user_id
    )

    assert result is not None


@pytest.mark.asyncio
async def test_delete_main_admin_cascades_children(
    school_admin_repository: SchoolAdminRepository,
    school_admin,
    child_school_admin
):
    await school_admin_repository.delete(
        SchoolAdmin.user_id == school_admin.user_id
    )

    result = await school_admin_repository.get_admin(
        child_school_admin.user_id
    )

    assert result is None
