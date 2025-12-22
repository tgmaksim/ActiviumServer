from database import Database

from . entities import VersionsResult


__all__ = ['get_latest_version', 'get_previous_versions']


async def get_latest_version() -> VersionsResult:
    """Данные о последней доступной версии приложения"""

    sql = """
            SELECT
                version,
                version_string,
                date,
                version_status,
                update_logs
            FROM versions
            WHERE version = (SELECT MAX(version) FROM versions)
          """
    result = await Database.fetch_row(sql)

    return VersionsResult(
        latestVersionNumber=result['version'],
        latestVersionString=result['version_string'],
        date=result['date'],
        versionStatus=result['version_status'],
        updateLogs=result['update_logs']
    )


async def get_previous_versions() -> list[VersionsResult]:
    """Данные о предыдущих версиях приложения"""

    sql = """
            SELECT
                version,
                version_string,
                date,
                version_status,
                update_logs
            FROM versions
          """
    results = await Database.fetch_all(sql)

    return [VersionsResult(
        latestVersionNumber=result['version'],
        latestVersionString=result['version_string'],
        date=result['date'],
        versionStatus=result['version_status'],
        updateLogs=result['update_logs']
    ) for result in results]
