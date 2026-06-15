from datetime import date
from typing import TypedDict


class DataWithDateType(TypedDict):
    date: date


class DataWithDataAndValueType(DataWithDateType):
    value: int


class CumulativeUsersType(DataWithDataAndValueType):
    pass


class DataWithDataAndGroupValue(DataWithDateType):
    parents: int
    children: int


class DailyRegistrationType(DataWithDataAndGroupValue):
    pass


class DailyActionsType(DataWithDataAndGroupValue):
    pass


class UniqueUsersDailyType(DataWithDataAndValueType):
    pass


class ClassDistributionType(TypedDict):
    class_name: str
    count: int
