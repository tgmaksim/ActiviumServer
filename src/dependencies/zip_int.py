import string


__all__ = ['zip_int']


def zip_int(number: int) -> str:
    """
    Перевод числа в систему счисления с основанием 36

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
