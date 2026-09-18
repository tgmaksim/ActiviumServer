from enum import StrEnum, auto


__all__ = ['ModuleList']


class ModuleList(StrEnum):
    start = auto()
    admin = auto()
    app = auto()
    help = auto()
    menu = auto()
    reviews = auto()
    school = auto()
    school_stats = auto()
    school_admins = auto()
    school_bells = auto()
    school_ea = auto()
    school_posts = auto()
