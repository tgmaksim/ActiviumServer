import string

from typing import Optional


__all__ = ['zip_int', 'unzip_int']


def zip_int(number: int) -> str:
    """
    Перевод числа в систему счисления с основанием 36 для представления его в "сжатом формате"

    >>> zip_int(36)
    '10'
    >>> int('10', 36)
    36

    :param number: число для перевода
    :return: число в 36-ричной системе счисления
    """

    if number == 0:
        return '0'

    alphabet = string.digits + string.ascii_lowercase
    base36 = ''

    while number:
        number, i = divmod(number, 36)
        base36 = alphabet[i] + base36

    return base36


def unzip_int(number: str) -> Optional[int]:
    """
    Перевод числа из "сжатого формата" (в системе счисления с основанием 36) в десятичную

    >>> zip_int(36)
    '10'
    >>> unzip_int('10')
    36
    >>> int('10', 36)
    36

    :param number: число в "сжатотом формате" (в системе счисления с основанием 36)
    :return: исходное число, если входное число валидно, иначе None
    """

    try:
        return int(number, 36)
    except (TypeError, ValueError):
        return None
