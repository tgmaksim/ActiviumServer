from .school_admin_error import SchoolAdminError
from src.dependencies.httpx import get_httpx_client
from dnevnikru import AioDnevnikruApi, DnevnikruApiException

from src.models.school_admin_model import SchoolAdmin
from src.support.repositories.school_admin_repository import SchoolAdminRepository


__all__ = ['check_school_admin']


async def check_school_admin(user_id: int, school_admin_repository: SchoolAdminRepository, check_auth: bool = False) -> SchoolAdmin:
    """
    Получение администратора образовательной организации по его идентификатору.
    Если администратора не существует или его сессия не работает, то выбрасывается исключение SchoolAdminError

    :param user_id: идентификатор администратора образовательной организации
    :param school_admin_repository: объект ``SchoolAdminRepository``
    :param check_auth: проверить авторизацию в Дневнике.ру
    :raise SchoolAdminError: сессия не существует или не авторизована
    :return: администратор образовательной организации, если он в порядке
    """

    school_admin = await school_admin_repository.get_admin(user_id)
    if school_admin is None:
        raise SchoolAdminError(user_id=user_id)

    if school_admin.dnevnik_admin.life is False:
        raise SchoolAdminError(user_id=user_id)

    if check_auth:
        dnr = AioDnevnikruApi(get_httpx_client(), school_admin.dnevnik_admin.dnevnik_token)

        try:
            await dnr.get_context()
        except DnevnikruApiException:
            raise SchoolAdminError(user_id=user_id)

    return school_admin
