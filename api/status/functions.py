from typing import Optional

from database import Database

from . entities import VersionsResult


__all__ = ['get_latest_version', 'get_previous_versions']

version_statuses = {
    0: (default_version_status := "Небольшие улучшения"),
    1: "Новая функция",
    2: "Требуется обновить",
}


async def get_latest_version(version_number: Optional[int] = None) -> VersionsResult:
    """
    Данные о последней доступной версии приложения

    :param version_number: номер сборки приложения для получения всех промежуточных версий
    :return: данные о последней доступной версии приложения
    """

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

    if version_number:
        # Статус версии определяется максимальным из всех промежуточных между данной и последней
        sql = "SELECT MAX(version_status) FROM versions WHERE version > $1"
        version_status = await Database.fetch_row_for_one(sql, version_number)
        if version_status:
            result['version_status'] = version_status

    return VersionsResult(
        latestVersionNumber=result['version'],
        latestVersionString=result['version_string'],
        date=result['date'],
        versionStatus=version_statuses.get(result['version_status'], default_version_status),
        updateLogs=result['update_logs']
    )


async def get_previous_versions() -> list[VersionsResult]:
    """
    Данные о предыдущих версиях приложения

    :return: данные о предыдущих версиях приложения
    """

    sql = """
            SELECT
                version,
                version_string,
                date,
                version_status,
                update_logs
            FROM versions
            ORDER BY version DESC
          """
    results = await Database.fetch_all(sql)

    return [VersionsResult(
        latestVersionNumber=result['version'],
        latestVersionString=result['version_string'],
        date=result['date'],
        versionStatus=version_statuses.get(result['version_status'], default_version_status),
        updateLogs=result['update_logs']
    ) for result in results]
