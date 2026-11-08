import secrets

from typing import Optional

from .reviews_service import ReviewsService
from ...config.project_config import settings
from ...services.html_response import HtmlResponse
from ...repositories.statistic_repository import StatName

from ...services.base_service import BaseService
from ..repositories.app_uow import AppUnitOfWork


__all__ = ['SiteService']


class SiteService(BaseService[AppUnitOfWork]):
    """Сервис для работы сайта"""

    async def get_root(self, session_id: Optional[str], likes_offset: Optional[int], likes_sort: Optional[str]) -> HtmlResponse:
        async with self.uow_factory() as uow:
            session = None
            if isinstance(session_id, str):
                session = await uow.session_repository.get_session(session_id)  # Получение сессии без проверки авторизации

            # Версии приложения
            latest_version = await uow.version_repository.get_latest_version()
            latest_web_version = await uow.web_version_repository.get_latest_version()

            # Режим сортировки отзывов
            mode = 'likes'
            if likes_sort in ('likes', 'max_stars', 'min_stars'):
                mode = likes_sort

            # Для обычной загрузки сайта отзывы без смещения в количестве 3.
            # При просмотре отзывов есть смещение, а лимит равен 10
            offset = 0
            limit = 3
            if isinstance(likes_offset, int) and likes_offset > 0:
                offset = likes_offset
                limit = 10

            # Отзывы, реакции пользователя на эти отзывы и offset для получения следующих отзывов
            reviews, liked_reviews, next_offset = await ReviewsService.get_top_reviews(uow, mode, offset, limit, session)
            csrf_token = secrets.token_urlsafe(32)  # Для постановки и удаления реакций на отзывах

            cookies = [
                {
                    'key': 'csrf_token',
                    'value': csrf_token,
                    'max_age': 5 * 60,  # 5 минут
                    'httponly': False,
                    'samesite': 'lax',
                },
                {
                    'key': 'session_id',
                    'value': session_id,
                    'max_age': 90 * 24 * 60 * 60,  # 90 дней
                    'httponly': True,
                    'secure': True,
                    'samesite': 'lax',
                }
            ]

            await uow.statistic_repository.add_statistic(session and session.parent_id, StatName.site)

            return HtmlResponse(
                name='main.html',
                context={
                    'project_name': settings.PROJECT_NAME_RU,
                    'project_url': settings.URL,
                    'server_version': settings.VERSION,
                    'version': "0.0.1" if latest_version is None else latest_version.version,
                    'date': '' if latest_version is None else latest_version.date,
                    'version_status': "Небольшие улучшения" if latest_version is None else latest_version.status,
                    'update_log': [] if latest_version is None else latest_version.logs.split('\n'),
                    'web_version': "0.0.1" if latest_web_version is None else latest_web_version.version,
                    'web_date': '' if latest_web_version is None else latest_web_version.date,
                    'web_version_status': "Небольшие улучшения" if latest_web_version is None else latest_web_version.status,
                    'web_update_log': [] if latest_web_version is None else latest_web_version.logs.split('\n'),
                    'reviews': [{
                        'id': review.parent_id,
                        'author': review.name,
                        'stars': review.stars,
                        'text': review.text,
                        'has_my_like': review.parent_id in liked_reviews,
                        'reactions': review.likes,
                        'created_at': review.created_at.strftime('%d.%m.%Y'),
                        'is_edited': review.is_updated
                    } for review in reviews],
                    'next_likes_offset': next_offset,
                    'likes_sort': mode,
                    'csrf_token': csrf_token,
                    'github': settings.GITHUB,
                    'github_server': settings.GITHUB_SERVER,
                },
                cookies=cookies
            )

    async def get_changelog(self, session_id: Optional[str]) -> HtmlResponse:
        async with self.uow_factory() as uow:
            session = None
            if isinstance(session_id, str):
                session = await uow.session_repository.get_session(session_id)  # Получение сессии без проверки авторизации

            # Версии приложения
            previous_versions = await uow.version_repository.get_all_versions(only_generic=False)
            previous_web_versions = await uow.web_version_repository.get_all_versions(only_generic=False)

            csrf_token = secrets.token_urlsafe(32)

            cookies = [
                {
                    'key': 'csrf_token',
                    'value': csrf_token,
                    'max_age': 5 * 60,  # 5 минут
                    'httponly': False,
                    'samesite': 'lax',
                },
                {
                    'key': 'session_id',
                    'value': session_id,
                    'max_age': 90 * 24 * 60 * 60,  # 90 дней
                    'httponly': True,
                    'secure': True,
                    'samesite': 'lax',
                }
            ]

            await uow.statistic_repository.add_statistic(session and session.parent_id, StatName.siteChangelog)

            return HtmlResponse(
                name='changelog.html',
                context={
                    'project_name': settings.PROJECT_NAME_RU,
                    'project_url': settings.URL,
                    'server_version': settings.VERSION,
                    'previous_versions': [{
                        'version': v.version,
                        'version_number': v.number,
                        'date': v.date,
                        'status': v.status,
                        'update_log': v.logs.split('\n'),
                    } for v in previous_versions],
                    'previous_web_versions': [{
                        'version': v.version,
                        'version_number': v.number,
                        'date': v.date,
                        'status': v.status,
                        'update_log': v.logs.split('\n'),
                    } for v in previous_web_versions],
                    'csrf_token': csrf_token
                },
                cookies=cookies
            )

    async def get_privacy(self, session_id: Optional[str]) -> HtmlResponse:
        async with self.uow_factory() as uow:
            session = None
            if isinstance(session_id, str):
                session = await uow.session_repository.get_session(session_id)  # Получение сессии без проверки авторизации

            await uow.statistic_repository.add_statistic(session and session.parent_id, StatName.sitePrivacy)

            return HtmlResponse(
                name="privacy.html",
                context={
                    'project_name': settings.PROJECT_NAME_RU,
                    'project_url': settings.URL
                }
            )

    async def get_terms(self, session_id: Optional[str]) -> HtmlResponse:
        async with self.uow_factory() as uow:
            session = None
            if isinstance(session_id, str):
                session = await uow.session_repository.get_session(session_id)  # Получение сессии без проверки авторизации

            await uow.statistic_repository.add_statistic(session and session.parent_id, StatName.siteTerms)

            return HtmlResponse(
                name="terms.html",
                context={
                    'project_name': settings.PROJECT_NAME_RU,
                    'project_url': settings.URL
                }
            )
