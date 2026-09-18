from ..enums.modules import ModuleList
from aiogram.filters.callback_data import CallbackData


__all__ = ['CallbackMenu']


class CallbackMenu(CallbackData, prefix=ModuleList.menu):
    pass
