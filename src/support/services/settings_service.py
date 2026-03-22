from typing import Callable, Optional

from httpx import AsyncClient
from dnevnikru import AioDnevnikruApi, BaseDnevnikruException

from ...dependencies.auth import check_session
from ...schemas.error_schema import ApiError
from ...services.base_service import BaseService
from ..repositories.app_uow import AppUnitOfWork

from ...models.parent_model import Parent
from ...api.session_error import SessionError

from ..schemas.settings_schemas import (
    Child,
    ChildrenResult,
    ChildrenApiResponse,
    UpdateFirebaseApiResponse,
    SwitchActiveChildApiResponse,
    StatusDnevnikNotificationsResult,
    StatusDnevnikNotificationsApiResponse,
    SwitchDnevnikNotificationsApiResponse,
)

__all__ = ['SettingsService']


class SettingsService(BaseService[AppUnitOfWork]):
    def __init__(self, uow_factory: Callable[[], AppUnitOfWork], httpx_client: AsyncClient):
        super().__init__(uow_factory)
        self.httpx_client = httpx_client

    async def getChildren(self, session_id: str) -> ChildrenApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)
            parent: Parent = session.parent

            dnr = AioDnevnikruApi(self.httpx_client, session.dnevnik_token)

            try:
                children = await dnr.get_children(parent.parent_id)
            except BaseDnevnikruException as e:
                if not await uow.session_repository.check_session_auth(session.session_id, dnr):
                    raise SessionError(session_id=session.session_id) from e
                raise

            await uow.statistic_repository.add_statistic(parent.parent_id, 'getChildren')

            return ChildrenApiResponse(
                answer=ChildrenResult(
                    children=[Child(
                        childId=int(child['id']),
                        name=child['shortName']
                    ) for child in children],
                    activeChildId=parent.active_child_id
                )
            )

    async def setActiveChild(self, session_id: str, child_id: int) -> SwitchActiveChildApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)
            parent: Parent = session.parent

            dnr = AioDnevnikruApi(self.httpx_client, session.dnevnik_token)

            if parent.active_child_id == child_id:
                await uow.statistic_repository.add_statistic(parent.parent_id, 'setActiveChild')
                return SwitchActiveChildApiResponse()

            try:
                children = await dnr.get_children(parent.parent_id)
            except BaseDnevnikruException as e:
                if not await uow.session_repository.check_session_auth(session.session_id, dnr):
                    raise SessionError(session_id=session.session_id) from e
                raise

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

                    await uow.child_repository.create_child(
                        child_id=child_id,
                        school_id=school_id,
                        group_id=group_id,
                        timezone=timezone
                    )
                    break

            await uow.parent_repository.set_active_child(parent.parent_id, child_id)

            await uow.statistic_repository.add_statistic(parent.parent_id, 'setActiveChild')

            return SwitchActiveChildApiResponse()

    async def getStatusDnevnikNotifications(self, session_id: str, child_id: Optional[int]) -> StatusDnevnikNotificationsApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)
            parent: Parent = session.parent

            if child_id is None:
                child_id = parent.active_child_id

            status = await uow.dnevnik_notification_repository.get_status(session_id, child_id)

            return StatusDnevnikNotificationsApiResponse(
                answer=StatusDnevnikNotificationsResult(
                    status=status is not None
                )
            )

    async def switchDnevnikNotifications(self, session_id: str, child_id: Optional[int], status: bool) -> SwitchDnevnikNotificationsApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)
            parent: Parent = session.parent

            if child_id is None:
                child_id = parent.active_child_id

            if not status:
                await uow.dnevnik_notification_repository.turn_off(session_id, child_id)
                await uow.statistic_repository.add_statistic(parent.parent_id, 'turnOffDnevnikNotifications')
                return SwitchDnevnikNotificationsApiResponse()

            dnr = AioDnevnikruApi(self.httpx_client, session.dnevnik_token)

            try:
                children = await dnr.get_children(parent.parent_id)
            except BaseDnevnikruException as e:
                if not await uow.session_repository.check_session_auth(session.session_id, dnr):
                    raise SessionError(session_id=session.session_id) from e
                raise

            if child_id != parent.active_child_id:
                try:
                    next(filter(lambda c: c['id'] == child_id, children))
                except StopIteration:
                    await uow.log_repository.add_log(
                        path='setActiveChild',
                        status=False,
                        session_id=session_id,
                        value=f"Ребенок {child_id} не найден"
                    )
                    return SwitchDnevnikNotificationsApiResponse(
                        status=False,
                        error=ApiError(
                            type="ValueError",
                            errorMessage="Ребенок не найден"
                        )
                    )

            if session.firebase_token is None:
                return SwitchDnevnikNotificationsApiResponse(
                    status=False,
                    error=ApiError(
                        type="ValueError",
                        errorMessage="Не указан firebase token для включения уведомлений"
                    )
                )

            await uow.dnevnik_notification_repository.turn_on(session_id, child_id)
            await uow.statistic_repository.add_statistic(parent.parent_id, 'turnOnDnevnikNotifications')

            return SwitchDnevnikNotificationsApiResponse()

    async def update_firebase(self, session_id: str, firebase_token: Optional[str]) -> UpdateFirebaseApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)
            parent: Parent = session.parent

            await uow.session_repository.update_firebase(session_id, firebase_token)

            await uow.statistic_repository.add_statistic(parent.parent_id, 'updateFirebase')

            return UpdateFirebaseApiResponse()
