from asyncio import gather
from typing import Callable, Optional

from yarl import URL
from httpx import AsyncClient

from dnevnikru import AioDnevnikruApi, BaseDnevnikruException
from ...config.project_config import settings

from ...dependencies.auth import check_session
from ...services.base_service import BaseService
from ..repositories.app_uow import AppUnitOfWork
from ...repositories.statistic_repository import StatName
from ...utils.referral_token import encode_referral_token

from ...models.parent_model import Parent
from ...models.session_model import Session

from ...schemas.error_schema import ApiError
from ...api.session_error import SessionError

from ..schemas.settings_schemas import (
    Child,
    ChildrenResult,
    ChildrenApiResponse,
    ReferralParamsResult,
    ReferralParamsApiResponse,
    UpdateFirebaseApiResponse,
    StatusEANotificationsResult,
    SwitchActiveChildApiResponse,
    StatusMarksNotificationsResult,
    StatusEANotificationsApiResponse,
    SwitchEANotificationsApiResponse,
    StatusMarksNotificationsApiResponse,
    SwitchMarksNotificationsApiResponse,
)


__all__ = ['SettingsService']


class SettingsService(BaseService[AppUnitOfWork]):
    """Сервис для управления настройками"""
    
    def __init__(self, uow_factory: Callable[[], AppUnitOfWork], httpx_client: AsyncClient):
        super().__init__(uow_factory)
        self.httpx_client = httpx_client

    async def getChildren(self, session_id: str) -> ChildrenApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)  # Проверка и получение сессии
            parent: Parent = session.parent

            dnr = AioDnevnikruApi(self.httpx_client, session.dnevnik_token)

            try:
                children, info = await gather(
                    dnr.get_children(parent.parent_id),
                    dnr.get_info()
                )
            except BaseDnevnikruException as e:  # Если возникла ошибка, проверяется авторизация сессии
                if not await uow.session_repository.check_session_auth(session.session_id, dnr):
                    raise SessionError(session_id=session.session_id) from e
                raise

            await uow.statistic_repository.add_statistic(parent.parent_id, StatName.getChildren)

            # Для родителя возвращаются дети, а для ребенка — собственный профиль
            return ChildrenApiResponse(
                answer=ChildrenResult(
                    children=[Child(
                        childId=int(child['id']),
                        name=child['shortName']
                    ) for child in children] or [Child(
                        childId=int(info['personId']),
                        name=info['shortName']
                    )],
                    activeChildId=session.active_child_id
                )
            )

    async def setActiveChild(self, session_id: str, child_id: int) -> SwitchActiveChildApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)  # Проверка и получение сессии
            parent: Parent = session.parent

            dnr = AioDnevnikruApi(self.httpx_client, session.dnevnik_token)

            try:
                children, info = await gather(
                    dnr.get_children(parent.parent_id),
                    dnr.get_info()
                )
            except BaseDnevnikruException as e:  # Если возникла ошибка, проверяется авторизация сессии
                if not await uow.session_repository.check_session_auth(session.session_id, dnr):
                    raise SessionError(session_id=session.session_id) from e
                raise

            # Если запрос от ребенка (владельца профиля)
            if parent.parent_id == child_id and len(children) == 0:
                return SwitchActiveChildApiResponse(
                    answer=ChildrenResult(
                        children=[Child(
                            childId=int(info['personId']),
                            name=info['shortName']
                        )],
                        activeChildId=child_id
                    )
                )

            # Проверка существования ребенка (профиля), которого требуется установить
            try:
                next(filter(lambda c: c['id'] == child_id, children))
            except StopIteration:
                await uow.log_repository.add_log(
                    path='setActiveChild',
                    status=False,
                    session_id=session_id,
                    value=f"Ребенок {child_id} не найден"
                )
                return SwitchActiveChildApiResponse(
                    status=False,
                    error=ApiError(
                        type="ValueError",
                        errorMessage="Ребенок не найден"
                    )
                )

            child = await uow.child_repository.get_child(child_id)

            # Если ребенок (профиль) еще не добавлен
            if child is None:
                context = await dnr.get_context()
                schools = context['schools']

                for context_child in context['children']:
                    if context_child['personId'] != child_id:
                        continue

                    schools_id: list[int] = context_child['schoolIds']
                    school: dict = next(filter(lambda s: s['type'] == 'Regular' and s['id'] in schools_id, schools))
                    school_id = int(school['id'])

                    groups_id: list[int] = school['groupIds']
                    groups: list[dict] = context['eduGroups']
                    group: dict = next(filter(lambda g: g['type'] == 'Group' and g['id'] in groups_id, groups))
                    group_id = int(group['id'])

                    user_child: dict = next(filter(lambda c: c['id'] == child_id, children))
                    info = await dnr.get_user_info(user_child['userId'])
                    hours, minutes = map(int, info['timezone'].split(':'))
                    timezone = (hours * 60 + minutes) * 60

                    # Создается ребенок (профиль)
                    await uow.child_repository.create_child(
                        child_id=child_id,
                        school_id=school_id,
                        group_id=group_id,
                        timezone=timezone
                    )
                    break

            await uow.session_repository.set_active_child(session_id, child_id)

            await uow.statistic_repository.add_statistic(parent.parent_id, StatName.setActiveChild)

            return SwitchActiveChildApiResponse(
                answer=ChildrenResult(
                    children=[Child(
                        childId=int(child['id']),
                        name=child['shortName']
                    ) for child in children],
                    activeChildId=child_id
                )
            )

    async def getStatusMarksNotifications(self, session_id: str, child_id: Optional[int]) -> StatusMarksNotificationsApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)  # Проверка и получение сессии

            # По умолчанию используется активный ребенок (профиль)
            if child_id is None:
                child_id = session.active_child_id

            status = await uow.marks_notification_repository.get_status(session_id, child_id)

            return StatusMarksNotificationsApiResponse(
                answer=StatusMarksNotificationsResult(
                    status=status is not None
                )
            )

    async def switchMarksNotifications(self, session_id: str, child_id: Optional[int], status: bool) -> SwitchMarksNotificationsApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)  # Проверка и получение сессии
            parent: Parent = session.parent

            # По умолчанию используется активный ребенок (профиль)
            if child_id is None:
                child_id = session.active_child_id

            if not status:
                await uow.marks_notification_repository.turn_off(session_id, child_id)
                await uow.statistic_repository.add_statistic(parent.parent_id, StatName.turnOffMarksNotifications)
                return SwitchMarksNotificationsApiResponse()

            # Проверка существования ребенка (профиля)
            if child_id != session.active_child_id:
                if not await self._check_child(uow, session, child_id):
                    return SwitchMarksNotificationsApiResponse(
                        status=False,
                        error=ApiError(
                            type="ValueError",
                            errorMessage="Ребенок не найден"
                        )
                    )

            await uow.marks_notification_repository.turn_on(session_id, child_id)
            await uow.statistic_repository.add_statistic(parent.parent_id, StatName.turnOnMarksNotifications)

            return SwitchMarksNotificationsApiResponse()

    async def update_firebase(self, session_id: str, firebase_token: str) -> UpdateFirebaseApiResponse:
        async with self.uow_factory() as uow:
            # Получение сессии, в том числе еще неавторизованной (без parent_id и других параметров) и неработающей
            session = await uow.session_repository.get_session(session_id, only_life=False)

            await uow.session_repository.update_firebase(session_id, firebase_token)

            await uow.statistic_repository.add_statistic(session.parent_id, StatName.updateFirebase)

            return UpdateFirebaseApiResponse()

    async def getStatusEANotifications(self, session_id: str, child_id: Optional[int]) -> StatusEANotificationsApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)  # Проверка и получение сессии

            # По умолчанию используется активный ребенок (профиль)
            if child_id is None:
                child_id = session.active_child_id

            status = await uow.ea_notification_repository.get_status(session_id, child_id)

            return StatusEANotificationsApiResponse(
                answer=StatusEANotificationsResult(
                    status=status is not None
                )
            )

    async def switchEANotifications(self, session_id: str, child_id: Optional[int], status: bool) -> SwitchEANotificationsApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)  # Проверка и получение сессии
            parent: Parent = session.parent

            # По умолчанию используется активный ребенок (профиль)
            if child_id is None:
                child_id = session.active_child_id

            if not status:
                await uow.ea_notification_repository.turn_off(session_id, child_id)
                await uow.statistic_repository.add_statistic(parent.parent_id, StatName.turnOffEANotifications)
                return SwitchEANotificationsApiResponse()

            # Проверка существования ребенка (профиля)
            if child_id != session.active_child_id:
                if not await self._check_child(uow, session, child_id):
                    return SwitchEANotificationsApiResponse(
                        status=False,
                        error=ApiError(
                            type="ValueError",
                            errorMessage="Ребенок не найден"
                        )
                    )

            await uow.ea_notification_repository.turn_on(session_id, child_id)
            await uow.statistic_repository.add_statistic(parent.parent_id, StatName.turnOnEANotifications)

            return SwitchEANotificationsApiResponse()

    async def _check_child(self, uow: AppUnitOfWork, session: Session, child_id: int) -> bool:
        """
        Проверка существования и связи ребенка (профиля) с пользователем

        :param uow: объект AppUnitOfWork для взаимодействия с БД
        :param session: сессия пользователя
        :param child_id: идентификатор проверяемого ребенка (профиля)
        :return: существует и принадлежит ли ребенок (профиль) пользователю
        """

        dnr = AioDnevnikruApi(self.httpx_client, session.dnevnik_token)

        try:
            children = await dnr.get_children(session.parent_id)
        except BaseDnevnikruException as e:
            if not await uow.session_repository.check_session_auth(session.session_id, dnr):
                raise SessionError(session_id=session.session_id) from e
            raise

        try:
            next(filter(lambda c: c['id'] == child_id, children))
        except StopIteration:
            await uow.log_repository.add_log(
                path='switchMarksNotifications',
                status=False,
                session_id=session.session_id,
                value=f"Ребенок {child_id} не найден"
            )
            return False

        return True

    async def getReferralParams(self, session_id: str) -> ReferralParamsApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)  # Проверка и получение сессии
            parent: Parent = session.parent

            me_referral = await uow.referral_repository.get_me_referral(parent.parent_id)  # Кто пригласил пользователя
            count_referrals = await uow.referral_repository.get_count_my_referrals(parent.parent_id)  # Сколько пригласил пользователь

            # Ссылка для приглашения
            link = URL(settings.URL).update_query(
                referral=encode_referral_token(parent.parent_id)
            )

            return ReferralParamsApiResponse(
                answer=ReferralParamsResult(
                    meReferralName=me_referral and me_referral.name,
                    referralsCount=count_referrals,
                    referralUrl=str(link)
                )
            )
