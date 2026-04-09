from ..schemas.status_schemas import VersionsApiResponse, VersionsResult, HealthApiResponse

from ...services.base_service import BaseService
from ..repositories.app_uow import AppUnitOfWork


__all__ = ['StatusService']


class StatusService(BaseService[AppUnitOfWork]):
    async def check_latest_version(self, version_number: int = None) -> VersionsApiResponse:
        async with self.uow_factory() as uow:
            latest = await uow.version_repository.get_latest_version()
            assert latest, "get_latest_version returned None"

            if version_number is not None:
                most_important = await uow.version_repository.get_most_important_version(version_number)

                if most_important is not None:
                    latest.status_id = most_important.status_id
                    latest.status = most_important.status

            await uow.statistic_repository.add_statistic(None, 'check_version')

            return VersionsApiResponse(
                answer=VersionsResult(
                    latestVersionNumber=latest.number,
                    latestVersionString=latest.version,
                    date=latest.date,
                    versionStatusId=latest.status_id,
                    versionStatus=latest.status,
                    updateLogs=latest.logs
                )
            )

    @classmethod
    async def health(cls) -> HealthApiResponse:
        return HealthApiResponse()
