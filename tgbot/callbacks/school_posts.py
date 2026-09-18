from typing import Optional, Literal

from aiogram import F
from aiogram.filters.callback_data import CallbackData, CallbackQueryFilter

from ..enums.modules import ModuleList


__all__ = ['CallbackSchoolPosts']

ACTION_TYPE = Literal['menu', 'post', 'create', 'delete', 'edit']


class CallbackSchoolPosts(CallbackData, prefix=ModuleList.school_posts):
    action: ACTION_TYPE = 'menu'
    offset: Optional[int] = None
    post_id: Optional[int] = None

    @classmethod
    def filter_action(cls, action: ACTION_TYPE) -> CallbackQueryFilter:
        return cls.filter(F.action == action)
