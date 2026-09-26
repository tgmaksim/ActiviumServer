from typing import Annotated

from fastapi import APIRouter, Depends, Query

from ..schemas.ads_schemas import (
    AdApiResponse,
    ClickAdApiResponse
)

from ..services.ads_service import AdsService
from ...dependencies.auth import get_session_id
from ...dependencies.services import get_ads_service


__all__ = ['router']

router = APIRouter(prefix='/ads', tags=["Ads"])
"""Router группы запросов ads"""


@router.post(
    "/checkAccessibleAd/0",
    summary="Получение доступной рекламы",
    description="Проверка наличия и получение рекламного объявления",
    response_model=AdApiResponse
)
async def _checkAccessibleAd0(
        sessionId: str = Depends(get_session_id),
        service: AdsService = Depends(get_ads_service)
) -> AdApiResponse:
    return await service.check_accessible_ad(sessionId)


@router.put(
    "/clickAd/0",
    summary="Записать клик на рекламу",
    description="Записать в статистику клик на рекламу и открытие связанного url",
    response_model=ClickAdApiResponse
)
async def _clickAd0(
        adId: Annotated[int, Query(description="Идентификатор рекламы")],
        sessionId: str = Depends(get_session_id),
        service: AdsService = Depends(get_ads_service)
) -> ClickAdApiResponse:
    return await service.click_ad(sessionId, adId)
