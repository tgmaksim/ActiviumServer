import secrets
import traceback

from asyncio import gather
from datetime import datetime, timedelta, UTC
from typing import Callable, Optional, Union, Literal, TypedDict

from yarl import URL
from httpx import AsyncClient

from sqlalchemy.exc import IntegrityError

from ...config.project_config import settings

from ..repositories.app_uow import AppUnitOfWork
from ...repositories.statistic_repository import StatName
from ..repositories.session_repository import SessionRepository
from ..repositories.information_repository import InformationRepository

from dnevnikru.aiodnevnikru.dnevnikru import AioDnevnikruApi

from ...services.base_service import BaseService
from ...services.html_response import HtmlResponse

from ..schemas.login_schemas import LoginApiResponse, LoginResult
from ..schemas.status_schemas import CheckSessionApiResponse, CheckSessionResult


__all__ = ['LoginService']


class AuthData(TypedDict):
    """Параметры авторизации ребенка"""

    person_id: int
    """Идентификатор персоны ребенка"""
    school_id: int
    """Идентификатор образовательной организации, в которой состоит ребенок"""
    group_id: int
    """Идентификатор учебной группы (класса) в образовательной организации"""
    timezone: int
    """Часовой пояс в секундах ребенка"""


class ResultAuth(TypedDict):
    """Параметры авторизации ребенка или всех детей родителя"""

    me: Optional[AuthData]
    """Параметры пользователя для только собственной авторизации"""
    children: Optional[list[AuthData]]
    """Параметры всех детей пользователя для авторизации родителя"""
    parent_id: Optional[int]
    """Идентификатор родителя"""


class LoginService(BaseService[AppUnitOfWork]):
    """Сервис для регистрации и авторизации"""

    def __init__(self, uow_factory: Callable[[], AppUnitOfWork], httpx_client: AsyncClient):
        super().__init__(uow_factory)
        self.httpx_client = httpx_client

    async def login(self, session_id: Optional[str], firebase_token: str) -> LoginApiResponse:
        async with self.uow_factory() as uow:
            # Если сессия передана и существует (даже если не работает), то она авторизуется повторно
            if session_id is None or await uow.session_repository.get_session(session_id, only_life=False) is None:
                session_id = await self._create_session(uow.session_repository)

            await uow.session_repository.update_firebase(session_id, firebase_token)

            # Ссылка для авторизации сессии в Дневнике.ру
            login_url = AioDnevnikruApi.build_login_url(
                dnevnikru_client_id=settings.DNEVNIK_CLIENT_ID,
                scope=["EducationalInfo", "CommonInfo", "FriendsAndRelatives"],
                redirect_uri=str(URL(settings.URL).joinpath("login/authSession")),
                state=session_id
            )

            await uow.statistic_repository.add_statistic(None, StatName.login)

            return LoginApiResponse(
                answer=LoginResult(
                    loginUrl=login_url,
                    sessionId=session_id
                )
            )

    @staticmethod
    async def _create_session(session_repository: SessionRepository) -> str:
        """
        Создание новой сессии

        :param session_repository: репозиторий для создания сессии
        :return: идентификатор новой сессии
        """

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

    @classmethod
    async def firstAuthSchoolAdmin(cls) -> HtmlResponse:
        return HtmlResponse(name='auth_session.html')

    async def secondAuthSession(self, dnevnik_token: str, session_id: str, referral_token: Optional[str]) -> HtmlResponse:
        # Функция для логирования
        log_exception = lambda error: uow.log_repository.add_log(
            path='secondAuthSession',
            status=False,
            session_id=session_id,
            value=error
        )

        async with self.uow_factory() as uow:
            # Проверка существования сессии, которую нужно авторизовать
            if await uow.session_repository.get_session(session_id, only_life=False) is None:
                await log_exception("Сессия не найдена")
                return HtmlResponse(
                    name='error.html',
                    status_code=500,
                    context={
                        'summary': "Произошла ошибка авторизации",
                        'description': "Сессия не найдена, попробуйте еще раз"
                    }
                )

            # Получение параметров для авторизации сессии пользователя
            try:
                dnevnik_data, parent_name = await self._dnevnik_auth(dnevnik_token)
                assert dnevnik_data is not None, "Данные авторизации пустые"
            except Exception as e:
                await log_exception('\n'.join(traceback.format_exception(e)))
                return HtmlResponse(
                    name='error.html',
                    status_code=500,
                    context={
                        'summary': "Произошла ошибка авторизации",
                        'description': "Произошла ошибка при получении основных данных от дневника.ру. Авторизация прервана"
                    }
                )

            # Учитель, не являющийся родителем не может пользовать приложением
            if dnevnik_data == 'teacher':
                await uow.log_repository.add_log(
                    path='secondAuthSession',
                    session_id=session_id,
                    value="Попытка регистрации учителя"
                )
                return HtmlResponse(
                    name='auth_session_error.html',
                    status_code=403,
                    context={
                        'reason': f"Учитель, не являющийся родителем, не может пользоваться приложением {settings.PROJECT_NAME}. "
                                  "Если вы является администратором образовательного учреждения и хотите выставлять новости "
                                  "и объявлять о мероприятиях для обучающихся своей организации, то сделайте это в "
                                  f"<a href=\"{settings.BOT_URL}\">Telegram-боте</a>"
                    }
                )

            # Если пользователь был приглашен, то записывается этот факт
            parent_referral_id = None
            if referral_token:
                try:
                    parent_referral_id = int(referral_token, 16)
                except (ValueError, TypeError):
                    pass
                else:
                    parent_referral = await uow.parent_repository.get_parent(parent_referral_id)
                    if parent_referral is None:
                        parent_referral_id = None

            # Авторизация сессии с полученными данными
            await self._auth_session(uow, session_id, dnevnik_token, dnevnik_data, parent_name, parent_referral_id)

            return HtmlResponse(
                name='auth_session_success.html',
                cookies=[{
                    'key': 'session_id',
                    'value': session_id,
                    'max_age': 30 * 24 * 60 * 60,  # 30 дней
                    'httponly': True,
                    'secure': True
                }]
            )

    async def _dnevnik_auth(self, dnevnik_token: str) -> tuple[Union[Optional[ResultAuth], Literal["teacher"]], str]:
        """
        Получение данных для авторизации сессии из Дневника.ру

        :param dnevnik_token: API-токен Дневника.ру для взаимодействия с ним
        :return: параметры для авторизации сессии (см. документацию к ResultAuth),
        'teacher', если пользователь является только учителем, None, если роль пользователя не определена;
        имя пользователя
        """

        dnr = AioDnevnikruApi(self.httpx_client, dnevnik_token)

        context: dict = await dnr.get_context()

        person_id = int(context['personId'])
        parent_name = context['shortName']
        schools: list[dict] = context['schools']
        roles = list(map(str, context['roles']))

        result: ResultAuth = ResultAuth(
            me=None,
            children=None,
            parent_id=None
        )

        # Если пользователь является ребенком
        if 'EduStudent' in roles:
            info = await dnr.get_info()
            hours, minutes = map(int, info['timezone'].split(':'))
            timezone = (hours * 60 + minutes) * 60

            schools_id: list[int] = context['schoolIds']
            school: dict = next(filter(lambda s: s['type'] == 'Regular' and s['id'] in schools_id, schools))
            school_id = int(school['id'])

            groups_id: list[int] = school['groupIds']
            groups: list[dict] = context['eduGroups']
            group: dict = next(filter(lambda g: g['type'] == 'Group' and g['id'] in groups_id, groups))
            group_id = int(group['id'])

            result['me'] = AuthData(
                person_id=person_id,
                school_id=school_id,
                group_id=group_id,
                timezone=timezone
            )
        # Если пользователь является родителем (может быть учителем также)
        elif 'EduParent' in roles and context['children']:
            children_data: list[AuthData] = []
            children: list[dict] = context['children']

            users_children = await dnr.get_children(person_id)
            infos: list[dict] = await gather(*[dnr.get_user_info(child['userId']) for child in users_children])

            # Возвращается информация о каждом ребенке
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

                children_data.append(AuthData(
                    person_id=int(child['personId']),
                    school_id=school_id,
                    group_id=group_id,
                    timezone=timezone
                ))

            result['children'] = children_data
            result['parent_id'] = person_id
        # Пользователь является только учителем или администратором образовательной организации
        elif 'EduStaff' in roles or 'EduSchoolAdministrator' in roles:
            return 'teacher', parent_name
        else:
            return None, parent_name  # Роль пользователя не определена

        return result, parent_name

    @classmethod
    async def _auth_session(
            cls,
            uow: AppUnitOfWork,
            session_id: str,
            dnevnik_token: str,
            dnevnik_data: ResultAuth,
            parent_name: str,
            parent_referral_id: Optional[int]
    ):
        """
        Авторизация сессии с данными

        :param uow: AppUnitOfWork для взаимодействия с БД
        :param session_id: идентификатор сессии, которую нужно авторизовать
        :param dnevnik_token: API-токен Дневника.ру для взаимодействия с ним
        :param dnevnik_data: полученные данные для авторизации
        :param parent_name: имя пользователя
        :param parent_referral_id: идентификатор пользователя, пригласившего при регистрации
        """

        registration = False

        person_id: int

        # Авторизация ребенка (владельца профиля)
        if me := dnevnik_data['me']:
            person_id = me['person_id']
            active_child_id = me['person_id']
            school_id = me['school_id']
            group_id = me['group_id']
            timezone = me['timezone']

            # Регистрация пользователя и его профиля (профиль может быть уже зарегистрирован)
            if await uow.parent_repository.get_parent(person_id) is None:
                await uow.child_repository.create_child(person_id, school_id, group_id, timezone, security=True)
                await uow.parent_repository.create_parent(person_id)

                registration = True
            # Обновление данных профиля, если они изменились
            else:
                child = await uow.child_repository.get_child(person_id)
                if child.school_id != school_id or child.group_id != group_id or child.timezone != timezone:
                    await uow.child_repository.update_child(
                        person_id,
                        school_id=school_id,
                        group_id=group_id,
                        timezone=timezone
                    )
        # Авторизация родителя с его детьми
        else:
            person_id = dnevnik_data['parent_id']
            children = dnevnik_data['children']
            active_child_id = children[0]['person_id']

            # Регистрация пользователя и его детей (профилей) (профили могут быть уже зарегистрированы)
            if await uow.parent_repository.get_parent(person_id) is None:
                for child in children:
                    await uow.child_repository.create_child(
                        child['person_id'],
                        child['school_id'],
                        child['group_id'],
                        child['timezone'],
                        security=True
                    )
                await uow.parent_repository.create_parent(person_id)

                registration = True
            # Обновление данных профилей или добавление их в случае отсутствия
            else:
                for relevant_child in children:
                    child = await uow.child_repository.get_child(relevant_child['person_id'])

                    if (child.school_id != relevant_child['school_id'] or child.group_id != relevant_child['group_id']
                            or child.timezone != relevant_child['timezone']):
                        await uow.child_repository.create_child(
                            relevant_child['person_id'],
                            school_id=relevant_child['school_id'],
                            group_id=relevant_child['group_id'],
                            timezone=relevant_child['timezone'],
                            security=True
                        )

        await uow.session_repository.auth_session(session_id, dnevnik_token, person_id, active_child_id)
        await uow.statistic_repository.add_statistic(person_id, StatName.authorization)

        if registration:
            await uow.statistic_repository.add_statistic(person_id, StatName.registration)

            # Запись информации о приглашении
            if parent_referral_id and parent_referral_id != person_id:
                await uow.referral_repository.link_referral(parent_referral_id, person_id, parent_name)

            # Информирование о написании отзыва и о функции уведомлений о новых оценках через некоторое время
            await cls.create_review_information(uow.information_repository, person_id)
            await cls.create_marks_notifications_information(uow.information_repository, person_id)

    @classmethod
    async def create_review_information(cls, information_repository: InformationRepository, person_id: int):
        """Создание информационное оповещения через некоторое время о том, что можно написать отзыв"""

        time = datetime.now(UTC) + timedelta(weeks=1)
        type_ = "review"
        title = "❤️ Оцените Активиум"
        text = "Вы пользуетесь сервисом Активиум уже целую неделю. Оцените приложение в настройках. Мы будет очень рады!"
        await information_repository.create_information(person_id, type_, time, title, text)

    @classmethod
    async def create_marks_notifications_information(cls, information_repository: InformationRepository, person_id: int):
        """Создание информационное оповещения через некоторое время о том, что можно включить функцию уведомлений о новых оценках"""

        time = datetime.now(UTC) + timedelta(days=1)
        type_ = "marks_notifications"
        title = "🔔 Не пропустите оценки"
        text = "Включите уведомления о новых оценках в настройках, чтобы получать уведомления после выставления учителем"
        await information_repository.create_information(person_id, type_, time, title, text)

    async def secondAuthSchoolAdmin(self, dnevnik_token: str, user_id: int) -> HtmlResponse:
        # Функция для логирования
        log_exception = lambda error: uow.log_repository.add_log(
            path='secondAuthSchoolAdmin',
            status=False,
            session_id=str(user_id),
            value=error
        )

        async with self.uow_factory() as uow:
            # Получение параметров для авторизации администратора образовательной организации
            try:
                dnevnik_data = await self._school_admin_dnevnik_auth(dnevnik_token)
                assert dnevnik_data != 'no_admin', "Попытка авторизовать админа профилем не администратора"
                name, person_id, school_id, timezone = dnevnik_data
            except AssertionError as e:  # Необходимые права администратора образовательной организации не найдены
                await log_exception('\n'.join(traceback.format_exception(e)))
                return HtmlResponse(
                    name='auth_session_error.html',
                    status_code=403,
                    context={
                        'reason': "Авторизоваться в качестве администратора ОО может только профиль с соответствующими "
                                  "права в Дневнике.ру (EduSchoolAdministrator или EduStaff). Если Вы считаете, что "
                                  "такие права есть, то обратитесь в поддержку (на сайте или через бота)"
                    }
                )
            except Exception as e:
                await log_exception('\n'.join(traceback.format_exception(e)))
                return HtmlResponse(
                    name='error.html',
                    status_code=500,
                    context={
                        'summary': "Произошла ошибка авторизации",
                        'description': "Произошла ошибка при получении основных данных от дневника.ру. Авторизация прервана"
                    }
                )

            # Авторизация администратора образовательной организации с полученными данными
            await self._auth_school_admin(uow, user_id, name, person_id, school_id, timezone, dnevnik_token)

            return HtmlResponse(name='auth_school_admin_success.html', context={'redirect_url': settings.BOT_URL})

    async def _school_admin_dnevnik_auth(self, dnevnik_token: str) -> Union[tuple[str, int, int, int], Literal["no_admin"]]:
        """
        Получение данных из Дневника.ру для авторизации администратора образовательной организации

        :param dnevnik_token: API-токен Дневника.ру для взаимодействия с ним
        :return: параметры для авторизации администратора (имя, идентификатор персоны в Дневнике.ру, идентификатор
         образовательной организации, часовой пояс в секундах) или 'no_admin', если пользователь не имеет прав
        """

        dnr = AioDnevnikruApi(self.httpx_client, dnevnik_token)

        info: dict = await dnr.get_info()
        hours, minutes = map(int, info['timezone'].split(':'))
        timezone = (hours * 60 + minutes) * 60

        context: dict = await dnr.get_context()

        person_id = int(context['personId'])
        name = context['shortName']
        schools: list[dict] = context['schools']
        roles = list(map(str, context['roles']))

        # Необходимые роли
        if 'EduStaff' not in roles and 'EduSchoolAdministrator' not in roles:
            return "no_admin"

        schools_id: list[int] = context['schoolIds']
        school: dict = next(filter(lambda s: s['type'] == 'Regular' and s['id'] in schools_id, schools))
        school_id = int(school['id'])

        return name, person_id, school_id, timezone

    @classmethod
    async def _auth_school_admin(
            cls,
            uow: AppUnitOfWork,
            user_id: int,
            name: str,
            person_id: int,
            school_id: int,
            timezone: int,
            dnevnik_token: str
    ):
        """
        Авторизация администратора образовательной организации с данными

        :param uow: AppUnitOfWork для взаимодействия с БД
        :param user_id: идентификатор Telegram-аккаунта администратора образовательной организации
        :param name: имя администратора образовательной организации
        :param person_id: идентификатор персоны в Дневнике.ру
        :param school_id: идентификатор образовательной организации
        :param timezone: часовой пояс в секундах
        :param dnevnik_token: API-токен Дневника.ру для взаимодействия с ним
        """

        school_admin = await uow.school_admin_repository.get_admin(user_id)
        if school_admin is None:
            stat_name = StatName.registrationSchoolAdmin
        else:
            stat_name = StatName.authorizationSchoolAdmin

        # Создание старшего администратора образовательной организации
        await uow.school_admin_repository.create_admin(
            user_id,
            name,
            None,
            person_id,
            school_id,
            timezone,
            dnevnik_token
        )

        await uow.statistic_repository.add_statistic(user_id, stat_name)

    async def checkSession(self, session_id: str) -> CheckSessionApiResponse:
        async with self.uow_factory() as uow:
            session = await uow.session_repository.get_session(session_id)  # Получение сессии без проверки

            await uow.statistic_repository.add_statistic(session and session.parent_id, StatName.checkSession)

            if session is None:
                return CheckSessionApiResponse(
                    answer=CheckSessionResult(
                        exists=False,
                        auth=False
                    )
                )

            # Проверка авторизации сессии в Дневнике.ру
            auth = await uow.session_repository.check_session_auth(session_id)

            return CheckSessionApiResponse(
                answer=CheckSessionResult(
                    exists=True,
                    auth=auth
                )
            )
