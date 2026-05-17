from typing import TypedDict


__all__ = ['HoursType']

class HoursType(TypedDict):
    """hours в моделях"""

    start: str
    """Время начала в формате HH:MM"""
    end: str
    """Время окончания в формате HH:MM"""
    string: str
    """Общее представление для пользователя в формате start - end"""
