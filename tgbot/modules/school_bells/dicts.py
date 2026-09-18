from typing import TypedDict

from src.models.hours_type import HoursType


__all__ = ['InputBellsWebAppDataType']


class InputBellsWebAppDataType(TypedDict):
    months: list[int]
    weekdays: list[int]
    bells: list[HoursType]
