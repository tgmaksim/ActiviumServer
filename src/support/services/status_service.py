from typing import Union
from datetime import datetime, UTC, timedelta

from ...dependencies.auth import check_session
from ...repositories.statistic_repository import StatName
from ...services.base_service import BaseService
from ..repositories.app_uow import AppUnitOfWork

from ..schemas.status_schemas import (
    Message,
    VersionsResult,
    InformationResult,
    VersionsResult0x3,
    HealthApiResponse,
    VersionsApiResponse,
    VersionsApiResponse0x4,
    InformationApiResponse,
)


__all__ = ['StatusService']


class StatusService(BaseService[AppUnitOfWork]):
    """Сервис для статусных взаимодействий"""

    async def check_latest_version(self, version_number: int, api: int = None) -> Union[VersionsApiResponse0x4, VersionsApiResponse]:
        async with self.uow_factory() as uow:
            latest = await uow.version_repository.get_latest_version()
            assert latest, "get_latest_version returned None"

            generic_latest = await uow.version_repository.get_latest_generic_version()
            latest_mini_versions = await uow.version_repository.get_latest_mini_versions(generic_latest.number)

            most_important = await uow.version_repository.get_most_important_version(version_number)

            status_id = latest.status_id
            status = latest.status
            info = latest.info
            if most_important is not None:
                status_id = most_important.status_id
                status = most_important.status
                info = most_important.info

            logs = latest.logs
            if version_number < generic_latest.number or not latest_mini_versions:
                logs = generic_latest.logs
            elif version_number < latest.number:
                logs = '\n\n'.join(map(lambda v: v.logs, filter(lambda v: v.number > version_number, latest_mini_versions)))

            await uow.statistic_repository.add_statistic(None, StatName.checkVersion)

            if api == 0:
                response_type = VersionsApiResponse0x4
                result_type = VersionsResult0x3
            else:
                response_type = VersionsApiResponse
                result_type = VersionsResult

            return response_type(
                answer=result_type(
                    latestVersionNumber=latest.number,
                    latestVersionString=latest.version,
                    date=latest.date,
                    versionStatusId=status_id,
                    versionStatus=status,
                    info=info,
                    updateLogs=logs
                )
            )

    @classmethod
    async def health(cls) -> HealthApiResponse:
        return HealthApiResponse()

    async def check_info_notifications(self, session_id: str) -> InformationApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)

            _informations = await uow.information_repository.get_informations(session.parent_id)
            await uow.information_repository.delete_informations(session.parent_id)

            informations = []
            for info in _informations:
                if info.type == 'review':
                    review = await uow.review_repository.get_review(session.parent_id, only_is_open=False)
                    if review is not None:
                        continue  # Пользователь уже написал отзыв
                    await uow.information_repository.create_information(
                        session.parent_id,
                        'review',
                        datetime.now(UTC) + timedelta(weeks=1),
                        "❤️ Оцените Активиум",
                        "Вы уже давно пользуетесь сервисом Активиум. Оцените приложение в настройках. Мы будет очень рады!"
                    )

                informations.append(info)

            await uow.statistic_repository.add_statistic(session.parent_id, StatName.checkInfoNotifications)

            return InformationApiResponse(
                answer=InformationResult(
                    messages=[Message(
                        title=information.title,
                        text=information.text
                    ) for information in informations],
                )
            )
