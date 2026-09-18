from typing import Optional, Literal

from aiogram import F
from aiogram.filters.callback_data import CallbackData, CallbackQueryFilter

from ..enums.modules import ModuleList


__all__ = ['CallbackSchoolBells']


ACTION_TYPE = Literal['menu', 'item', 'add', 'edit', 'delete']


class CallbackSchoolBells(CallbackData, prefix=ModuleList.school_bells):
    action: ACTION_TYPE = 'menu'
    hour_id: Optional[int] = None

    @classmethod
    def filter_action(cls, action: ACTION_TYPE) -> CallbackQueryFilter:
        return cls.filter(F.action == action)
