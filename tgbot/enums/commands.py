from enum import StrEnum, auto


__all__ = ['CommandList']


class CommandList(StrEnum):
    reload = auto()
    start = auto()
    app = auto()
    help = auto()
    menu = auto()
    school = auto()
