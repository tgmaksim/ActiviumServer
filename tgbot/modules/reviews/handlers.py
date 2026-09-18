from aiogram import Router
from aiogram.types import CallbackQuery

from ...callbacks.reviews import CallbackReviews
from ...dependencies.services import ModuleService

from ...enums.modules import ModuleList

from firebase.messaging import FirebaseApiError

from src.services.log_service import LogService
from src.utils.exception import format_exception
from src.dependencies.uow import get_log_uow_factory
from src.support.services.reviews_service import ReviewsService


__all__ = ['router']

router = Router(name=ModuleList.reviews)


@router.callback_query(CallbackReviews.filter(), ModuleService(ReviewsService))
async def _review_moderation(callback_query: CallbackQuery, callback_data: CallbackReviews, service: ReviewsService):
    """Принятие решения о модерации отзыва"""

    try:
        publish = await service.resolve_review(callback_data.parent_id, callback_data.publish)
    except FirebaseApiError as e:
        service = LogService(get_log_uow_factory())
        await service.log(
            path='tgbot',
            status=False,
            value=format_exception(e)
        )

        await callback_query.answer()
        await callback_query.message.reply("Произошла ошибка")
    else:
        await callback_query.message.edit_reply_markup()
        await callback_query.message.reply(f"Отзыв {'опубликован' if publish else 'не прошел модерацию'}")
