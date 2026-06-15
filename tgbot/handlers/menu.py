from aiogram import Router, F

from ..utils.message_model import MessageModel
from aiogram.utils.formatting import Text, CustomEmoji

from src.dependencies.uow import get_app_uow_factory

from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)


__all__ = ['router']

router = Router()

uow_factory = get_app_uow_factory()


@router.message(Command('menu'))
async def _cmd_menu(message: Message):
    """Открытие меню администратора образовательной организации"""

    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(message.from_user.id)
        if school_admin is None:
            await message.answer("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        # Удаление клавиатурных кнопок
        await (await message.answer(".", reply_markup=ReplyKeyboardRemove())).delete()

        answer = admin_menu()
        await message.answer(**answer)


def admin_menu() -> MessageModel:
    """Меню администратора образовательной организации"""

    return MessageModel(
        text=Text(CustomEmoji("⚙️", custom_emoji_id="5341715473882955310"), " Меню администратора ОО"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Звонки", icon_custom_emoji_id="5458603043203327669", callback_data="admin_bells"),
             InlineKeyboardButton(text="Статистика", icon_custom_emoji_id="5231200819986047254", callback_data="admin_stats")],
            [InlineKeyboardButton(text="Внеурочные занятия", icon_custom_emoji_id="5265002646397285605", callback_data="admin_ea")],
            [InlineKeyboardButton(text="Новости и мероприятия", icon_custom_emoji_id="5382013970905309819", callback_data="school_posts|0")],
            [InlineKeyboardButton(text="Мои администраторы", icon_custom_emoji_id="5440712623219822019", callback_data="my_admins")],
            [InlineKeyboardButton(text="Назад", icon_custom_emoji_id="5467864676320681402", callback_data="start")]
        ])
    )


@router.callback_query(F.data == 'menu')
async def _callback_menu(callback_query: CallbackQuery):
    """Открытие меню кнопкой Назад"""

    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(callback_query.from_user.id)
        if school_admin is None:
            await callback_query.answer("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        answer = admin_menu()
        await callback_query.message.edit_text(**answer)


@router.callback_query(F.data == "admin_bells")
async def _bells(callback_query: CallbackQuery):
    """Добавление звонкового расписания, отличного от Дневника.ру"""

    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(callback_query.from_user.id)
        if school_admin is None:
            await callback_query.message.edit_text("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        await callback_query.answer("Данная функция в разработке", show_alert=True)


@router.callback_query(F.data == "admin_ea")
async def _admin_ea(callback_query: CallbackQuery):
    """Добавление расписания внеурочных занятий в образовательной организации"""

    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(callback_query.from_user.id)
        if school_admin is None:
            await callback_query.message.edit_text("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        await callback_query.answer("Данная функция в разработке", show_alert=True)
