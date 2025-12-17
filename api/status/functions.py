from database import Database

from . entities import VersionsResult

__all__ = ['get_latest_version']


async def get_latest_version() -> VersionsResult:
    """Последняя доступная версия приложения"""

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
