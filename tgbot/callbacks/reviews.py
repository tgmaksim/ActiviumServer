from ..enums.modules import ModuleList
from aiogram.filters.callback_data import CallbackData


__all__ = ['CallbackReviews']


class CallbackReviews(CallbackData, prefix=ModuleList.reviews):
    publish: bool
    parent_id: int
