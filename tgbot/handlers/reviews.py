import traceback

from aiogram import Router

from aiogram import F
from aiogram.types import CallbackQuery

from firebase.messaging import FirebaseApiError

from src.dependencies.httpx import get_httpx_client
from src.dependencies.uow import get_app_uow_factory, get_log_uow_factory
from src.dependencies.services import get_reviews_service

from src.services.log_service import LogService


__all__ = ['router']

router = Router()


@router.callback_query(F.data.startswith('open_review').__or__(F.data.startswith('block_review')))
async def review_moderation(callback_query: CallbackQuery):
    parent_id = int(callback_query.data.split('|')[1])
    service = get_reviews_service(get_app_uow_factory(), get_httpx_client())

    publish = callback_query.data.startswith('open_review')
    try:
        publish = await service.resolve_review(parent_id, publish)
    except FirebaseApiError as e:
        service = LogService(get_log_uow_factory())
        await service.log(
            path='tgbot',
            status=False,
            value='\n'.join(traceback.format_exception(e))
        )

        await callback_query.answer()
        await callback_query.message.reply("Произошла ошибка")
    else:
        await callback_query.message.edit_reply_markup()
        await callback_query.message.reply(f"Отзыв {'опубликован' if publish else 'не прошел модерацию'}")
