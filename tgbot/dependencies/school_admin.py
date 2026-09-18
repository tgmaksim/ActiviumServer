from typing import Optional

from dnevnikru import AioDnevnikruApi, DnevnikruApiException

from src.dependencies.httpx import get_httpx_client

from src.models import SchoolAdmin
from src.support.repositories.school_admin_repository import SchoolAdminRepository


__all__ = ['get_school_admin']


async def get_school_admin(user_id: int, school_admin_repository: SchoolAdminRepository, check_auth: bool = False) -> Optional[SchoolAdmin]:
    """
    Получение администратора образовательной организации по его идентификатору

    :param user_id: идентификатор администратора образовательной организации
    :param school_admin_repository: объект ``SchoolAdminRepository``
    :param check_auth: проверить авторизацию в Дневнике.ру
    :return: администратор образовательной организации, если он в порядке
    """

    school_admin = await school_admin_repository.get_admin(user_id)
    if school_admin is None:
        return None

    if school_admin.dnevnik_admin.life is False:
        return None

    if check_auth:
        dnr = AioDnevnikruApi(get_httpx_client(), school_admin.dnevnik_admin.dnevnik_token)

        try:
            await dnr.get_context()
        except DnevnikruApiException:
            return None

    return school_admin
