from aiogram.fsm.state import State, StatesGroup


__all__ = ['BellsStatesGroup']


class BellsStatesGroup(StatesGroup):
    """Группа состояний при изменении звонкового расписания образовательной организации"""

    create_or_edit_bell = State('create_or_edit_bell')
    """Ожидание сообщения от Web App с данными"""
