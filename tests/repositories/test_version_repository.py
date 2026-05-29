import pytest

from src.support.repositories.version_repository import VersionRepository


def version_factory(
    number: int,
    version: str,
    *,
    status_id: float = 0.5,
    status: str = "test",
    logs: str = "test logs",
    date: str = "09.12.2009",
    **kwargs
):
    return {
        "number": number,
        "version": version,
        "status_id": status_id,
        "status": status,
        "logs": logs,
        "date": date,
        **kwargs
    }


@pytest.fixture
def version_repository(session):
    return VersionRepository(session)


@pytest.fixture
async def versions(version_repository: VersionRepository):
    return await version_repository.create_many([
        version_factory(
            number=1,
            version="1.0.0",
            parent_version=None
        ),
        version_factory(
            number=2,
            version="1.0.1",
            parent_version=1
        )
    ])


@pytest.fixture
async def generic_version(version_repository: VersionRepository):
    return await version_repository.create(
        version_factory(
            number=1,
            version="1.0.0"
        )
    )


@pytest.mark.asyncio
async def test_create_many_versions(
    version_repository: VersionRepository
):
    version1, version2 = (
        await version_repository.create_many([
            version_factory(
                number=1,
                version="1.0.0",
                parent_version=None,
                info="Скачайте обновление"
            ),
            version_factory(
                number=2,
                version="1.0.1",
                parent_version=1,
                info=None
            )
        ])
    )

    assert version1.number == 1
    assert version2.number == 2

    assert version1.version == "1.0.0"
    assert version2.version == "1.0.1"

    assert version2.parent_version == version1.number

    assert version1.info is not None
    assert version2.info is None


@pytest.mark.asyncio
async def test_get_all_versions(
    version_repository: VersionRepository,
    versions
):
    result = await version_repository.get_all_versions(only_generic=False)

    assert len(result) == 2


@pytest.mark.asyncio
async def test_get_all_generic_versions(
    version_repository: VersionRepository,
    versions
):
    result = await version_repository.get_all_versions()

    assert len(result) == 1
    assert result[0].number == 1


@pytest.mark.asyncio
async def test_get_latest_version(
    version_repository: VersionRepository,
    versions
):
    result = await version_repository.get_latest_version()

    assert result is not None
    assert result.number == 2


@pytest.mark.asyncio
async def test_get_latest_generic_version(
    version_repository: VersionRepository,
    versions
):
    result = await version_repository.get_latest_generic_version()

    assert result is not None
    assert result.number == 1


@pytest.mark.asyncio
async def test_get_latest_mini_versions(
    version_repository: VersionRepository,
    versions
):
    g_version, _ = versions
    result = await version_repository.get_latest_mini_versions(g_version.number)

    assert len(result) == 1
    assert result[0].number == 2


@pytest.mark.asyncio
async def test_get_most_important_version(
    version_repository: VersionRepository,
    versions
):
    result = await version_repository.get_most_important_version(0)

    assert result is not None
    assert result.number == 1


@pytest.mark.asyncio
async def test_get_most_important_returns_none(
    version_repository: VersionRepository,
    generic_version
):
    result = await version_repository.get_most_important_version(999)

    assert result is None


@pytest.mark.asyncio
async def test_get_unknown_version_returns_empty(
    version_repository: VersionRepository
):
    result = await version_repository.get_all_versions(only_generic=False)

    assert result == []