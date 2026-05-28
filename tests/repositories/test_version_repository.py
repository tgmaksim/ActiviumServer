import pytest

from ..factories import version_factory

from src.support.repositories.version_repository import VersionRepository


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