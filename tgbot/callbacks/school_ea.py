from typing import Optional, Literal

from aiogram import F
from magic_filter import MagicFilter

from ..enums.modules import ModuleList
from .callback_filter import CallbackQueryFilter
from aiogram.filters.callback_data import CallbackData


__all__ = ['CallbackSchoolEA']

ACTION_TYPE = Literal['menu', 'list_ea', 'delete', 'confirm_delete', 'add', 'edit']


class CallbackSchoolEA(CallbackData, prefix=ModuleList.school_ea):
    action: ACTION_TYPE = 'menu'
    key: Optional[str] = None

    @classmethod
    def filter(cls, rule: Optional[MagicFilter] = None) -> CallbackQueryFilter:
        __doc__ = super.__doc__

        return CallbackQueryFilter(callback_data=cls, rule=rule)

    @classmethod
    def filter_action(cls, action: ACTION_TYPE) -> CallbackQueryFilter:
        return cls.filter(F.action == action)
