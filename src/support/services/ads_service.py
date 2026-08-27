import random

from datetime import timedelta
from typing import Callable, Optional

from yarl import URL
from httpx import AsyncClient

from ...models import Parent
from ...config.project_config import settings
from ...dependencies.auth import check_session
from ...schemas.error_schema import ApiError
from ...services.base_service import BaseService
from ..repositories.app_uow import AppUnitOfWork
from ...repositories.statistic_repository import StatName

from ..schemas.ads_schemas import (
    Ad,
    AdResult,
    AdApiResponse,
    ClickAdApiResponse
)


__all__ = ['AdsService']

MIN_LAST_VIEWING_DELTA = timedelta(days=1)


class AdsService(BaseService[AppUnitOfWork]):
    """Сервис для рекламного взаимодействия"""

    def __init__(self, uow_factory: Callable[[], AppUnitOfWork], httpx_client: AsyncClient):
        super().__init__(uow_factory)
        self.httpx_client = httpx_client

    async def check_accessible_ad(self, session_id: str) -> AdApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)  # Проверка и получение сессии
            parent: Parent = session.parent

            school_id = session.active_child.school_id
            group_id = session.active_child.group_id

            ads = await uow.ad_repository.get_accessible_ads(parent.parent_id, school_id, group_id, MIN_LAST_VIEWING_DELTA)

            new_ads_ids: list[int] = []  # Еще не увиденные рекламные объявления
            seen_ads: list[tuple[int, timedelta]] = []  # Когда-то увиденные рекламные объявления

            for ad_id, last_viewing_delta in ads:
                if last_viewing_delta is None:
                    new_ads_ids.append(ad_id)
                else:
                    seen_ads.append((ad_id, last_viewing_delta))

            chosen_id: Optional[int] = None

            # Если есть еще не увиденные рекламные объявления, то показывается случайное из них
            if new_ads_ids:
                chosen_id: int = random.choice(new_ads_ids)

            # Если еще не увиденных рекламных объявлений нет, то случайно выбирается
            elif seen_ads:
                weights: list[float] = []
                ad_ids_pool: list[int] = []

                for ad_id, last_viewing_delta in seen_ads:
                    ad_ids_pool.append(ad_id)

                    # Веса, пропорциональные времени от прошлого просмотра
                    seconds_since_view = max(last_viewing_delta.total_seconds(), 1)  # Защита от деления на 0 или отрицательных весов
                    weights.append(seconds_since_view)

                chosen_id: int = random.choices(ad_ids_pool, weights=weights, k=1)[0]

            if chosen_id:
                chosen_ad = await uow.ad_repository.get_ad(chosen_id)

                if chosen_ad.has_image:
                    image_url = str(URL(settings.URL).joinpath('ads', str(chosen_ad.ad_id), 'image.png'))
                else:
                    image_url = str(URL(settings.URL).joinpath('ads', 'default.png'))

            else:
                chosen_ad = None
                image_url = None

            if chosen_id:
                await uow.ad_repository.see_ad(chosen_id)
                await uow.ad_viewing_repository.see_ad(chosen_id, parent.parent_id)

            await uow.statistic_repository.add_statistic(session.parent_id, StatName.checkAccessibleAd)

            return AdApiResponse(
                answer=AdResult(
                    ad=Ad(
                        adId=chosen_ad.ad_id,
                        title=chosen_ad.title,
                        text=chosen_ad.text,
                        imageUrl=image_url,
                        url=chosen_ad.url
                    ) if chosen_ad else None,
                )
            )

    async def click_ad(self, session_id: str, ad_id: int) -> ClickAdApiResponse:
        async with self.uow_factory() as uow:
            session = await check_session(session_id, uow.session_repository)  # Проверка и получение сессии

            ad = await uow.ad_repository.get_ad(ad_id)

            if ad is None:
                return ClickAdApiResponse(
                    status=False,
                    error=ApiError(
                        type="AdNotFoundError",
                        errorMessage="Рекламное объявление не найдено"
                    )
                )

            await uow.ad_repository.click_ad(ad_id)

            await uow.statistic_repository.add_statistic(session.parent_id, StatName.clickAd)

            return ClickAdApiResponse()
