from typing import Union
from datetime import datetime, UTC, timedelta

from ...config.project_config import settings
from ...dependencies.auth import check_session
from ...services.base_service import BaseService
from ..repositories.app_uow import AppUnitOfWork
from ...repositories.statistic_repository import StatName

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
            latest = await uow.version_repository.get_latest_version()  # Самая последняя версия
            assert latest, "get_latest_version returned None"

            # Последняя общая версия и ее мини-версии (например, 1.1.0; 1.1.1, 1.1.2)
            generic_latest = await uow.version_repository.get_latest_generic_version()
            latest_mini_versions = await uow.version_repository.get_latest_mini_versions(generic_latest.number)

            # Самая важная (с наибольшим status_id) версия
            most_important = await uow.version_repository.get_most_important_version(version_number)

            # В качестве важности версии и информационного сообщения к ней используются данные самой важной версии
            status_id = latest.status_id
            status = latest.status
            info = latest.info
            if most_important is not None:
                status_id = most_important.status_id
                status = most_important.status
                info = most_important.info

            logs = latest.logs
            # Если текущая версия меньше последней общей или общая версия - самая последняя
            if version_number < generic_latest.number or not latest_mini_versions:
                logs = generic_latest.logs
            # Текущая версия не меньше последней общей, но не является самой новой
            elif version_number < latest.number:
                # Список изменений складывается из всех изменений последних мини-версий
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
                    info=info,  # Для VersionsResult0x3 игнорируется
                    updateLogs=logs
                )
            )

    @classmethod
    async def health(cls) -> HealthApiResponse:
        return HealthApiResponse()

    async def check_info_notifications(self, session_id: str) -> InformationApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)  # Проверка и получение сессии

            # Получение информационных оповещений и удаление их
            _informations = await uow.information_repository.get_informations(session.parent_id)
            await uow.information_repository.delete_informations(session.parent_id)

            informations = []
            for info in _informations:
                if info.type == 'review':
                    review = await uow.review_repository.get_review(session.parent_id, only_is_open=False)
                    if review is not None:
                        continue  # Пользователь уже написал отзыв, оповещение не требуется
                    # В следующий раз, если отзыв еще не написан, уведомление повторится с похожим текстом
                    await uow.information_repository.create_information(
                        session.parent_id,
                        'review',
                        datetime.now(UTC) + timedelta(weeks=1),
                        f"❤️ Оцените {settings.PROJECT_NAME_RU}",
                        f"Вы уже давно пользуетесь сервисом {settings.PROJECT_NAME_RU}. Оцените приложение в настройках. Мы будет очень рады!"
                    )

                if info.type == 'marks_notifications':
                    status = await uow.marks_notification_repository.get_status(session.session_id, session.active_child_id)
                    if status is not None:
                        continue  # Пользователь уже включил уведомления, оповещение не требуется
                    # В следующий раз, если функция выключена, уведомление повторится
                    await uow.information_repository.create_information(
                        session.parent_id,
                        'marks_notifications',
                        datetime.now(UTC) + timedelta(days=1),
                        "🔔 Не пропустите оценки",
                        "Включите уведомления о новых оценках в настройках, чтобы получать уведомления после выставления учителем"
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
