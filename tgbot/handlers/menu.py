from aiogram import Router, F
from aiogram.enums import ContentType

from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, \
    KeyboardButton, KeyboardButtonRequestUsers, ReplyKeyboardRemove

from src.dependencies.uow import get_app_uow_factory


__all__ = ['router']

from src.repositories.statistic_repository import StatName

from src.support.repositories.app_uow import AppUnitOfWork

router = Router()


@router.message(Command('menu'))
async def _cmd_menu(message: Message):
    uow_factory = get_app_uow_factory()
    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(message.from_user.id)
        if school_admin is None:
            await message.answer("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        answer = admin_menu()
        await message.answer(**answer)


def admin_menu() -> dict:
    return {
        'text': "<tg-emoji emoji-id=\"5341715473882955310\">⚙️</tg-emoji> Меню администратора школы",
        'reply_markup': InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Звонки", icon_custom_emoji_id="5458603043203327669", callback_data="admin_bells"),
             InlineKeyboardButton(text="Статистика", icon_custom_emoji_id="5231200819986047254", callback_data="admin_stats")],
            [InlineKeyboardButton(text="Внеурочные занятия", icon_custom_emoji_id="5265002646397285605", callback_data="admin_ea")],
            [InlineKeyboardButton(text="Новости и мероприятия", icon_custom_emoji_id="5382013970905309819", callback_data="admin_posts")],
            [InlineKeyboardButton(text="Мои администраторы", icon_custom_emoji_id="5440712623219822019", callback_data="my_admins")],
            [InlineKeyboardButton(text="Назад", icon_custom_emoji_id="5467864676320681402", callback_data="start")]])}


@router.callback_query(F.data == 'menu')
async def _callback_menu(callback_query: CallbackQuery):
    uow_factory = get_app_uow_factory()
    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(callback_query.from_user.id)
        if school_admin is None:
            await callback_query.answer("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        answer = admin_menu()
        await callback_query.message.edit_text(**answer)


@router.callback_query(F.data == "admin_bells")
async def _bells(callback_query: CallbackQuery):
    uow_factory = get_app_uow_factory()
    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(callback_query.from_user.id)
        if school_admin is None:
            await callback_query.message.edit_text("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        await callback_query.answer("Данная функция в разработке", show_alert=True)


@router.callback_query(F.data == "admin_stats")
async def _admin_stats(callback_query: CallbackQuery):
    uow_factory = get_app_uow_factory()
    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(callback_query.from_user.id)
        if school_admin is None:
            await callback_query.message.edit_text("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        await callback_query.answer("Данная функция в разработке", show_alert=True)


@router.callback_query(F.data == "admin_ea")
async def _admin_ea(callback_query: CallbackQuery):
    uow_factory = get_app_uow_factory()
    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(callback_query.from_user.id)
        if school_admin is None:
            await callback_query.message.edit_text("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        await callback_query.answer("Данная функция в разработке", show_alert=True)


@router.callback_query(F.data == "admin_posts")
async def _admin_ea(callback_query: CallbackQuery):
    uow_factory = get_app_uow_factory()
    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(callback_query.from_user.id)
        if school_admin is None:
            await callback_query.message.edit_text("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        await callback_query.answer("Данная функция в разработке", show_alert=True)


@router.callback_query(F.data == "my_admins")
async def _my_admins(callback_query: CallbackQuery):
    uow_factory = get_app_uow_factory()
    async with uow_factory() as uow:
        answer = await menu_my_admins(uow, callback_query.from_user.id)
        await callback_query.message.edit_text(answer['text'], reply_markup=answer.get('reply_markup'))


async def menu_my_admins(uow: AppUnitOfWork, user_id: int) -> dict:
    school_admin = await uow.school_admin_repository.get_admin(user_id)
    if school_admin is None:
        return {'text': "Меню Активиум доступно только администраторам ОО\nДля подключения: /school"}

    my_admins = await uow.school_admin_repository.get_my_admins(user_id)
    buttons = [[InlineKeyboardButton(text=admin.name, icon_custom_emoji_id="5210952531676504517", callback_data=f"delete_my_admin|{admin.user_id}")] for admin in my_admins]
    buttons.append([InlineKeyboardButton(text="Добавить администратора", icon_custom_emoji_id="5397916757333654639", callback_data="add_admin")])
    buttons.append([InlineKeyboardButton(text="Назад", icon_custom_emoji_id="5467864676320681402", callback_data="menu")])

    return {'text': "<tg-emoji emoji-id=\"5440712623219822019\">✅</tg-emoji> Мои администраторы",
            'reply_markup': InlineKeyboardMarkup(inline_keyboard=buttons)}


@router.callback_query(F.data == "add_admin")
async def _add_admin(callback_query: CallbackQuery):
    uow_factory = get_app_uow_factory()
    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(callback_query.from_user.id)
        if school_admin is None:
            await callback_query.message.edit_text(
                "Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        await callback_query.message.answer(
            "Отправьте пользователя (или несколько), которому будет выдано разрешение на администрирование",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Выбрать пользователя(ей)",
                                          request_users=KeyboardButtonRequestUsers(
                                              request_id=0, user_is_bot=False, request_name=True, max_quantity=10))],
                          [KeyboardButton(text="Отмена")]],
                is_persistent=True, resize_keyboard=True, one_time_keyboard=True, input_field_placeholder="Выберите кнопкой"))
        await callback_query.message.delete()


@router.message((F.content_type == ContentType.USERS_SHARED).__add__(F.users_shared.request_id == 0))
async def _add_admin(message: Message):
    users = [(user.user_id, ' '.join([user.first_name, user.last_name or '']).strip()) for user in message.users_shared.users]

    uow_factory = get_app_uow_factory()
    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(message.from_user.id)
        if school_admin is None:
            await message.answer("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        await (await message.answer(".", reply_markup=ReplyKeyboardRemove())).delete()

        my_admins = await uow.school_admin_repository.get_my_admins(message.from_user.id)
        if len(my_admins) + len(users) > 5:
            await message.answer("Превышен лимит администраторов (5)")
        else:
            await uow.school_admin_repository.add_my_admins(message.from_user.id, users)
            await uow.statistic_repository.add_statistic(message.from_user.id, StatName.addSchoolAdminFrom)

        answer = await menu_my_admins(uow, message.from_user.id)
        await message.answer(**answer)


@router.callback_query(F.data.startswith("delete_my_admin"))
async def _delete_admin(callback_query: CallbackQuery):
    admin_id = int(callback_query.data.split("|")[1])

    uow_factory = get_app_uow_factory()
    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(callback_query.from_user.id)
        if school_admin is None:
            await callback_query.answer("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        await uow.school_admin_repository.delete_my_admin(callback_query.from_user.id, admin_id)
        await uow.statistic_repository.add_statistic(callback_query.from_user.id, StatName.deleteSchoolAdminFrom)

        answer = await menu_my_admins(uow, callback_query.from_user.id)
        await callback_query.message.edit_text(**answer)
