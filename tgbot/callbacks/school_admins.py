from typing import Optional, Literal

from aiogram import F
from aiogram.filters.callback_data import CallbackData, CallbackQueryFilter

from ..enums.modules import ModuleList


__all__ = ['CallbackSchoolAdmins']

ACTION_TYPE = Literal['menu', 'add', 'delete']


class CallbackSchoolAdmins(CallbackData, prefix=ModuleList.school_admins):
    action: ACTION_TYPE = 'menu'
    user_id: Optional[int] = None

    @classmethod
    def filter_action(cls, action: ACTION_TYPE) -> CallbackQueryFilter:
        return cls.filter(F.action == action)
