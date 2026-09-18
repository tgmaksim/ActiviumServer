from typing import Literal

from aiogram import F
from aiogram.filters.callback_data import CallbackData, CallbackQueryFilter

from ..enums.modules import ModuleList


__all__ = ['CallbackSchoolStats']

ACTION_TYPE = Literal['menu', 'create']


class CallbackSchoolStats(CallbackData, prefix=ModuleList.school_stats):
    action: ACTION_TYPE = 'menu'

    @classmethod
    def filter_action(cls, action: ACTION_TYPE) -> CallbackQueryFilter:
        return cls.filter(F.action == action)
