from typing import Optional


__all__ = ['encode_referral_token', 'decode_referral_token']


def encode_referral_token(parent_id: int) -> str:
    """
    Создание токена для приглашения из идентификатора пользователя

    >>> parent_id = 12345
    >>> token = encode_referral_token(parent_id)
    >>> assert token == hex(parent_id)[2:]

    :param parent_id: идентификатор пользователя
    :return: токен для приглашения
    """

    return hex(parent_id)[2:]


def decode_referral_token(token: str) -> Optional[int]:
    """
    Декодирование токена для приглашения

    >>> token = "3039"
    >>> parent_id = decode_referral_token(token)
    >>> assert parent_id == int(token, 16)

    :param token: токен для приглашения
    :return: parent_id - идентификатор пользователя
    """

    try:
        return int(token, 16)
    except (TypeError, ValueError):
        return None
