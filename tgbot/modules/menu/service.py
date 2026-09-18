from typing import Optional

from ...enums.emoji import EmojiList
from aiogram.utils.formatting import Text

from src.models import SchoolAdmin
from src.services.base_service import BaseService
from src.support.repositories.app_uow import AppUnitOfWork

from ...enums.commands import CommandList
from ...modules.menu.buttons import menu_buttons
from ...schemas.service_result import ServiceResult


__all__ = ['MenuService']


class MenuService(BaseService[AppUnitOfWork]):
    """Сервис для открытия меню администратора образовательной организации"""

    async def menu(self, user_id: int) -> ServiceResult:
        school_admin = await self._get_admin(user_id)

        if school_admin is None:
            return ServiceResult(
                text=Text(
                    "Меню Активиум доступно только администраторам ОО\n"
                    f"Для подключения: /{CommandList.school}"
                )
            )

        if school_admin.dnevnik_admin.life is False:
            admin_type = "Ваша сессия" if school_admin.parent_admin_id is None else "Сессия старшего"
            return ServiceResult(
                text=Text(
                    f"{admin_type} администратора ОО истекла и требует повторной авторизации\n"
                    f"Для этого откройте /{CommandList.school} и повторите или выберите другой способ авторизации"
                )
            )

        answer = self.admin_menu()
        answer.service_params.delete_keyboard = True

        return answer

    async def _get_admin(self, user_id: int) -> Optional[SchoolAdmin]:
        async with self.uow_factory() as uow:
            return await uow.school_admin_repository.get_admin(user_id, only_life=False)

    @staticmethod
    def admin_menu() -> ServiceResult:
        text = Text(EmojiList.settings.value, "Меню администратора ОО")
        reply_markup = menu_buttons()

        return ServiceResult(text=text, reply_markup=reply_markup)

