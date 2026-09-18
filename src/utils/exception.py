import traceback


__all__ = ['format_exception']


def format_exception(e: BaseException):
    return '\n'.join(traceback.format_exception(e))
