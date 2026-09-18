from .buttons import my_admins_buttons
from .constants import MY_ADMINS_LIMIT

from ...enums.emoji import EmojiList
from aiogram.utils.formatting import Text
from ...schemas.service_result import ServiceResult, ServiceParams

from src.services.base_service import BaseService
from src.repositories.statistic_repository import StatName
from src.support.repositories.app_uow import AppUnitOfWork


__all__ = ['MyAdminsService']


class MyAdminsService(BaseService[AppUnitOfWork]):
    """Сервис для взаимодействия со своим списком дочерних администраторов"""

    async def my_admins(self, user_id: int) -> ServiceResult:
        async with self.uow_factory() as uow:
            my_admins = await uow.school_admin_repository.get_my_admins(user_id)

        text = Text(
            EmojiList.verified.value, "Мои администраторы"
        )

        reply_markup = my_admins_buttons([(school_admin.user_id, school_admin.name) for school_admin in my_admins])

        return ServiceResult(text=text, reply_markup=reply_markup)

    async def add_my_admins(self, user_id: int, new_my_admins: list[tuple[int, str]]) -> ServiceResult:
        async with self.uow_factory() as uow:
            my_admins = await uow.school_admin_repository.get_my_admins(user_id)

            if len(my_admins) + len(new_my_admins) > MY_ADMINS_LIMIT:
                text = Text(
                    f"Превышен лимит администраторов ({MY_ADMINS_LIMIT})"
                )
                return ServiceResult(text=text)

            await uow.school_admin_repository.add_my_admins(user_id, new_my_admins)

            await uow.statistic_repository.add_statistic(user_id, StatName.addSchoolAdminFrom)

        return ServiceResult(service_params=ServiceParams(delete_message=True))

    async def delete_my_admin(self, user_id: int, admin_id: int):
        async with self.uow_factory() as uow:
            await uow.school_admin_repository.delete_my_admin(user_id, admin_id)

            await uow.statistic_repository.add_statistic(user_id, StatName.deleteSchoolAdminFrom)
