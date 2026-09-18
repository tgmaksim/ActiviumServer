from aiogram.fsm.state import State, StatesGroup


__all__ = ['AddMyAdminsStatesGroup']


class AddMyAdminsStatesGroup(StatesGroup):
    """Группа состояний при добавлении дочернего администратора образовательной организации"""

    users_shared = State('users_shared')
    """Ожидание сообщения с пользователями"""
