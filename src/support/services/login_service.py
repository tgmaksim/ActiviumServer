import secrets
import traceback

from asyncio import gather
from typing import Callable, Optional, Union, Literal

from yarl import URL
from httpx import AsyncClient

from sqlalchemy.exc import IntegrityError

from dnevnikru.exceptions import BaseDnevnikruException
from dnevnikru.aiodnevnikru.dnevnikru import AioDnevnikruApi
from ..schemas.status_schemas import CheckSessionApiResponse, CheckSessionResult

from ...services.html_response import HtmlResponse
from ..schemas.login_schemas import LoginApiResponse, LoginResult

from ...config.project_config import settings
from ...services.base_service import BaseService
from ..repositories.app_uow import AppUnitOfWork
from ..repositories.session_repository import SessionRepository


__all__ = ['LoginService']


class LoginService(BaseService[AppUnitOfWork]):
    def __init__(self, uow_factory: Callable[[], AppUnitOfWork], httpx_client: AsyncClient):
        super().__init__(uow_factory)
        self.httpx_client = httpx_client

    async def login(self, session_id: Optional[str], firebase_token: str) -> LoginApiResponse:
        async with self.uow_factory() as uow:
            if session_id is None or await uow.session_repository.get_session(session_id) is None:
                session_id = await self._create_session(uow.session_repository)

            await uow.session_repository.update_firebase(session_id, firebase_token)

            login_url = AioDnevnikruApi.build_login_url(
                dnevnikru_client_id=settings.DNEVNIK_CLIENT_ID,
                scope=["EducationalInfo", "CommonInfo", "FriendsAndRelatives"],
                redirect_uri=str(URL(settings.URL).joinpath("login/authSession")),
                state=session_id
            )

            await uow.statistic_repository.add_statistic(None, 'login')

            return LoginApiResponse(
                answer=LoginResult(
                    loginUrl=login_url,
                    sessionId=session_id
                )
            )

    @staticmethod
    async def _create_session(session_repository: SessionRepository) -> str:
        for i in range(10):
            session_id = secrets.token_hex(16)
            try:
                await session_repository.create_session(session_id)
                return session_id
            except IntegrityError:
                continue

        raise RuntimeError('session creation failed')

    @classmethod
    async def firstAuthSession(cls) -> HtmlResponse:
        return HtmlResponse(name='auth_session.html')

    async def secondAuthSession(self, dnevnik_token: str, session_id: str) -> HtmlResponse:
        log_exception = lambda error: uow.log_repository.add_log(
            path='secondAuthSession',
            status=False,
            session_id=session_id,
            value=error
        )

        async with self.uow_factory() as uow:
            if await uow.session_repository.get_session(session_id) is None:
                await log_exception("Сессия не найдена")
                return HtmlResponse(
                    name='error.html',
                    status_code=500,
                    context={
                        'summary': "Произошла ошибка авторизации",
                        'description': "Сессия не найдена, попробуйте еще раз"
                    }
                )

            try:
                dnevnik_data = await self._dnevnik_auth(dnevnik_token)
                assert dnevnik_data is not None, "Данные авторизации пустые"
            except (BaseDnevnikruException, KeyError, IndexError, StopIteration, AssertionError) as e:
                await log_exception('\n'.join(traceback.format_exception(e)))
                return HtmlResponse(
                    name='error.html',
                    status_code=500,
                    context={
                        'summary': "Произошла ошибка авторизации",
                        'description': "Произошла ошибка при получении основных данных от дневника.ру. Авторизация прервана"
                    }
                )

            if dnevnik_data == 'teacher':
                return HtmlResponse(
                    name='auth_session_error.html',
                    status_code=403,
                    context={
                        'reason': f"Учитель, не являющийся родителем, не может пользоваться приложением {settings.PROJECT_NAME}. "
                                  "Если вы является администратором школы или колледжа и хотите выставлять новости "
                                  "и объявлять о мероприятиях для обучающихся своей организации, то сделайте это в "
                                  f"<a href=\"{settings.BOT_URL}\">Telegram-боте</a>"
                    }
                )

            await self._auth_session(uow, session_id, dnevnik_token, dnevnik_data)

            return HtmlResponse(
                name='auth_session_success.html',
                cookies={
                    'key': 'session_id',
                    'value': session_id,
                    'max_age': 30 * 24 * 60 * 60,  # 30 дней
                    'httponly': True,
                    'secure': True
                }
            )

    async def _dnevnik_auth(self, dnevnik_token: str) -> Union[Optional[dict[str, ...]], Literal["teacher"]]:
        dnr = AioDnevnikruApi(self.httpx_client, dnevnik_token)

        context: dict = await dnr.get_context()

        person_id = int(context['personId'])
        schools: list[dict] = context['schools']
        roles = list(map(str, context['roles']))

        result: dict[str, ...] = {
            'me': None,
            'children': None,
            'parent': None
        }

        if 'EduStudent' in roles:
            info: dict = await dnr.get_info()
            hours, minutes = map(int, info['timezone'].split(':'))
            timezone = (hours * 60 + minutes) * 60

            schools_id: list[int] = context['schoolIds']
            school: dict = next(filter(lambda s: s['type'] == 'Regular' and s['id'] in schools_id, schools))
            school_id = int(school['id'])

            groups_id: list[int] = school['groupIds']
            groups: list[dict] = context['eduGroups']
            group: dict = next(filter(lambda g: g['type'] == 'Group' and g['id'] in groups_id, groups))
            group_id = int(group['id'])

            result['me'] = {
                'person_id': person_id,
                'school_id': school_id,
                'group_id': group_id,
                'timezone': timezone
            }
        elif 'EduParent' in roles and context['children']:
            children_data: list[dict[str, int]] = []
            children: list[dict] = context['children']

            users_children = await dnr.get_children(person_id)
            infos: list[dict] = await gather(*[dnr.get_user_info(child['userId']) for child in users_children])

            for child in children:
                schools_id: list[int] = child['schoolIds']
                school: dict = next(filter(lambda s: s['type'] == 'Regular' and s['id'] in schools_id, schools))
                school_id = int(school['id'])

                groups_id: list[int] = child['groupIds']
                groups: list[dict] = context['eduGroups']
                group: dict = next(filter(lambda g: g['type'] == 'Group' and g['id'] in groups_id, groups))
                group_id = int(group['id'])

                info: dict = next(filter(lambda i: i['personId'] == child['personId'], infos))
                hours, minutes = map(int, info['timezone'].split(':'))
                timezone = (hours * 60 + minutes) * 60

                children_data.append({
                    'person_id': int(child['personId']),
                    'school_id': school_id,
                    'group_id': group_id,
                    'timezone': timezone
                })

            result['children'] = children_data
            result['parent_id'] = person_id
        elif 'EduTeacher' in roles:
            return 'teacher'
        else:
            return None

        return result

    @classmethod
    async def _auth_session(cls, uow: AppUnitOfWork, session_id: str, dnevnik_token: str, dnevnik_data: dict):
        if me := dnevnik_data['me']:
            person_id: int = me['person_id']
            school_id: int = me['school_id']
            group_id: int = me['group_id']
            timezone: int = me['timezone']

            if await uow.parent_repository.get_parent(person_id) is None:
                await uow.child_repository.create_child(person_id, school_id, group_id, timezone, security=True)
                await uow.parent_repository.create_parent(person_id, person_id)

                await uow.statistic_repository.add_statistic(person_id, 'registration')
            else:
                child = await uow.child_repository.get_child(person_id)
                if child.school_id != school_id or child.group_id != group_id or child.timezone != timezone:
                    await uow.child_repository.update_child(
                        person_id,
                        school_id=school_id,
                        group_id=group_id,
                        timezone=timezone
                    )
        else:
            person_id: int = dnevnik_data['parent_id']
            children: list[dict] = dnevnik_data['children']

            if await uow.parent_repository.get_parent(person_id) is None:
                for child in children:
                    await uow.child_repository.create_child(
                        child['person_id'],
                        child['school_id'],
                        child['group_id'],
                        child['timezone'],
                        security=True
                    )
                await uow.parent_repository.create_parent(person_id, children[0]['person_id'])

                await uow.statistic_repository.add_statistic(person_id, 'registration')
            else:
                for relevant_child in children:
                    child = await uow.child_repository.get_child(relevant_child['person_id'])

                    if (child.school_id != relevant_child['school_id'] or child.group_id != relevant_child['group_id']
                            or child.timezone != relevant_child['timezone']):
                        await uow.child_repository.update_child(
                            relevant_child['person_id'],
                            school_id=relevant_child['school_id'],
                            group_id=relevant_child['group_id'],
                            timezone=relevant_child['timezone']
                        )

        await uow.session_repository.auth_session(session_id, dnevnik_token, person_id)
        await uow.statistic_repository.add_statistic(person_id, 'authorization')

    async def checkSession(self, session_id: str) -> CheckSessionApiResponse:
        async with self.uow_factory() as uow:
            session = await uow.session_repository.get_session(session_id)

            await uow.statistic_repository.add_statistic(session and session.parent_id, 'checkSession')

            if session is None:
                return CheckSessionApiResponse(
                    answer=CheckSessionResult(
                        exists=False,
                        auth=False
                    )
                )

            auth = await uow.session_repository.check_session_auth(session_id)

            return CheckSessionApiResponse(
                answer=CheckSessionResult(
                    exists=True,
                    auth=auth
                )
            )
