from aiogram.fsm.state import StatesGroup, State


__all__ = ['CreatePostStatesGroup']


class CreatePostStatesGroup(StatesGroup):
    """Группа состояний при создании поста"""

    title = State('title')
    """Ожидание сообщения с заголовком поста"""
    description = State('description')
    """Ожидание сообщения с описанием поста"""
    image = State('image')
    """Ожидание сообщения с главной картинкой поста"""
    show_schedule_date = State('show_schedule_date')
    """Ожидание сообщения с датой мероприятия для поста"""
    content = State('content')
    """Ожидание сообщения с содержанием поста"""
