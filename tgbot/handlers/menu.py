from yarl import URL
from pathlib import Path

from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest

from src.repositories.statistic_repository import StatName

from tgbot.config import settings
from src.support.repositories.app_uow import AppUnitOfWork

from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ReplyKeyboardMarkup, \
    KeyboardButton, KeyboardButtonRequestUsers, ReplyKeyboardRemove, LinkPreviewOptions

from src.dependencies.uow import get_app_uow_factory


__all__ = ['router']

router = Router()

MY_ADMINS_LIMIT = 5
SHOWN_POSTS_LIMIT = 5

POST_TITLE_LIMIT = 128
POST_DESCRIPTION_LIMIT = 256


class AddMyAdminsStatesGroup(StatesGroup):
    users_shared = State('users_shared')


class CreatePostStatesGroup(StatesGroup):
    title = State('title')
    description = State('description')
    image = State('image')
    show_schedule_date = State('show_schedule_date')
    content = State('content')


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
            [InlineKeyboardButton(text="Новости и мероприятия", icon_custom_emoji_id="5382013970905309819", callback_data="admin_posts|0")],
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


@router.callback_query(F.data.startswith("admin_posts|"))
async def _admin_posts(callback_query: CallbackQuery):
    offset = int(callback_query.data.split("|")[1])

    uow_factory = get_app_uow_factory()
    async with uow_factory() as uow:
        answer = await menu_school_posts(uow, callback_query.from_user.id, offset)

        try:
            await callback_query.message.edit_text(**answer)
        except TelegramBadRequest as e:
            if "message is not modified" in e.message:
                await callback_query.answer()
            else:
                raise


async def menu_school_posts(uow: AppUnitOfWork, user_id: int, offset: int) -> dict:
    school_admin = await uow.school_admin_repository.get_admin(user_id)
    if school_admin is None:
        return {'text': "Меню Активиум доступно только администраторам ОО\nДля подключения: /school"}

    posts = await uow.school_post_repository.get_school_posts(
        school_admin.admin_school_id,
        offset=offset,
        limit=SHOWN_POSTS_LIMIT + 1
    )
    right_offset = offset + SHOWN_POSTS_LIMIT
    left_offset = max(0, offset - SHOWN_POSTS_LIMIT)

    buttons = [[InlineKeyboardButton(
        text=post.title[:32],
        callback_data=f"school_post|{post.post_id}|{offset}"
    )] for i, post in enumerate(posts) if i < SHOWN_POSTS_LIMIT]

    buttons.append([
        InlineKeyboardButton(text=" ", icon_custom_emoji_id="5877536313623711363" if left_offset != offset else None,
                             callback_data=f"admin_posts|{left_offset}"),
        InlineKeyboardButton(text=" ", icon_custom_emoji_id="5030872266716480568",
                             callback_data=f"admin_posts|{offset}"),
        InlineKeyboardButton(text=" ", icon_custom_emoji_id="5875506366050734240" if len(posts) > SHOWN_POSTS_LIMIT else None,
                             callback_data=f"admin_posts|{right_offset}")
    ])

    buttons.append([InlineKeyboardButton(text="Создать публикацию", icon_custom_emoji_id="5397916757333654639", callback_data="create_post")])
    buttons.append([InlineKeyboardButton(text="Назад", icon_custom_emoji_id="5467864676320681402", callback_data="menu")])

    return {'text': "<tg-emoji emoji-id=\"5382013970905309819\">🎙</tg-emoji> Новости и мероприятия",
            'reply_markup': InlineKeyboardMarkup(inline_keyboard=buttons)}


@router.callback_query(F.data.startswith("school_post|"))
async def _school_post(callback_query: CallbackQuery):
    post_id, offset = map(int, callback_query.data.split("|")[1:])

    uow_factory = get_app_uow_factory()
    async with uow_factory() as uow:
        answer = await menu_school_post(uow, callback_query.from_user.id, post_id, f"school_post|{post_id}|{offset}")
        try:
            await callback_query.message.edit_text(**answer)
        except TelegramBadRequest as e:
            if "message is not modified" in e.message:
                await callback_query.answer()
            else:
                raise


async def menu_school_post(uow: AppUnitOfWork, user_id: int, post_id: int, callback: str) -> dict:
    school_admin = await uow.school_admin_repository.get_admin(user_id)
    if school_admin is None:
        return {'text': "Меню Активиум доступно только администраторам ОО\nДля подключения: /school"}

    post = await uow.school_post_repository.get_post(post_id)
    if post is None:
        return await menu_school_posts(uow, user_id, 0)

    image_relative_path = ('posts', 'images', f'{post_id}.jpg')
    image_url = str(URL(settings.URL).joinpath(*image_relative_path))

    preview_options = LinkPreviewOptions(
        is_disabled=False,
        url=settings.TELEGRAM_PREVIEW_URL + image_url,
        prefer_large_media=True
    ) if post.has_image else None

    text = (f"<b>{post.title}</b>\n"
            f"{post.description}\n\n"
            f"Публикация от {post.created_at.strftime('%e %b.')}\n"
            f"В расписании: {post.schedule_date.strftime('%e %b.')}\n"
            f"Обновлено: {'да' if post.is_updated else 'нет'}\n"
            f"Заходы: {post.count_clicks}\n"
            f"Просмотры: {post.count_viewings}\n"
            f"Реакции: {post.count_likes}")

    post_relative_path = ('posts', post_id)
    url = str(URL(settings.URL).joinpath(*post_relative_path))

    buttons = [[InlineKeyboardButton(text="Посмотреть", icon_custom_emoji_id="5210956306952758910", url=url),
                InlineKeyboardButton(text="Редактировать", icon_custom_emoji_id="5395444784611480792", callback_data=f"edit_post|{post_id}")],
               [InlineKeyboardButton(text="Удалить публикацию", icon_custom_emoji_id="5210952531676504517", callback_data=f"delete_post|{post_id}")],
               [InlineKeyboardButton(text="Назад", icon_custom_emoji_id="5467864676320681402", callback_data=callback)]]

    return {'text': text, 'link_preview_options': preview_options,
            'reply_markup': InlineKeyboardMarkup(inline_keyboard=buttons)}


@router.callback_query(F.data == "create_post")
async def _create_post(callback_query: CallbackQuery, state: FSMContext):
    uow_factory = get_app_uow_factory()
    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(callback_query.from_user.id)
        if school_admin is None:
            await callback_query.message.edit_text("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        await callback_query.message.answer(
            f"Вы начали создание поста\nОтправьте заголовок (от 1 до {POST_TITLE_LIMIT} символов)\n"
            "В любой момент нажмите на кнопку Отмена для сброса операции",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Отмена", icon_custom_emoji_id="5210952531676504517")]],
                resize_keyboard=True
            )
        )
        await state.set_state(CreatePostStatesGroup.title)
        await callback_query.message.delete()


@router.message(CreatePostStatesGroup.title)
async def _create_post(message: Message, state: FSMContext):
    uow_factory = get_app_uow_factory()
    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(message.from_user.id)
        if school_admin is None:
            await state.clear()
            await message.answer("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        if message.text == "Отмена":
            await state.clear()
            await (await message.answer(".", reply_markup=ReplyKeyboardRemove())).delete()
            answer = await menu_school_posts(uow, message.from_user.id, 0)
            await message.answer(**answer)
            return

        if message.content_type != ContentType.TEXT:
            await message.answer("Отправьте заголовок статьи!")
            return

        if (len_text := len(message.text)) > POST_TITLE_LIMIT:
            await message.answer(f"Вы превысили лимит длины заголовка ({len_text})")
            return

        await state.update_data(title=message.text)

        await message.answer(
            f"Отлично! Теперь отправьте короткое описание (от 1 до {POST_DESCRIPTION_LIMIT} символов), "
            "которое будет сопровождать заголовок. Если оно не требуется, нажмите на кнопку Пропустить",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Пропустить", icon_custom_emoji_id="5416117059207572332")],
                          [KeyboardButton(text="Отмена", icon_custom_emoji_id="5210952531676504517")]],
                resize_keyboard=True
            )
        )

        await state.set_state(CreatePostStatesGroup.description)


@router.message(CreatePostStatesGroup.description)
async def _create_post(message: Message, state: FSMContext):
    uow_factory = get_app_uow_factory()
    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(message.from_user.id)
        if school_admin is None:
            await state.clear()
            await message.answer("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        if message.text == "Отмена":
            await state.clear()
            await (await message.answer(".", reply_markup=ReplyKeyboardRemove())).delete()
            answer = await menu_school_posts(uow, message.from_user.id, 0)
            await message.answer(**answer)
            return

        if message.content_type != ContentType.TEXT:
            await message.answer("Отправьте описание статьи!")
            return

        if (len_text := len(message.text)) > POST_DESCRIPTION_LIMIT:
            await message.answer(f"Вы превысили лимит длины заголовка ({len_text})")
            return

        await state.update_data(description=None if message.text == "Пропустить" else message.text)

        await message.answer(
            f"Продолжим. Отправьте главную фотографию статьи. Если она не требуется, нажмите на кнопку Пропустить",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Пропустить", icon_custom_emoji_id="5416117059207572332")],
                          [KeyboardButton(text="Отмена", icon_custom_emoji_id="5210952531676504517")]],
                resize_keyboard=True
            )
        )

        await state.set_state(CreatePostStatesGroup.image)


@router.message(CreatePostStatesGroup.image)
async def _create_image(message: Message, state: FSMContext):
    uow_factory = get_app_uow_factory()
    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(message.from_user.id)
        if school_admin is None:
            await state.clear()
            await message.answer("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        if message.text == "Отмена":
            await state.clear()
            await (await message.answer(".", reply_markup=ReplyKeyboardRemove())).delete()
            answer = await menu_school_posts(uow, message.from_user.id, 0)
            await message.answer(**answer)
            return

        if message.content_type != ContentType.PHOTO:
            await message.answer("Отправьте фото статьи!")
            return

        image_relative_path = ('temp', 'posts', 'images', f'{message.from_user.id}.jpg')
        path = Path(settings.WWW_PATH, *image_relative_path)

        await message.answer("Фото загружается <tg-emoji emoji-id=\"5235997383627658618\">🔵</tg-emoji>")

        try:
            photo = max(message.photo, key=lambda ph: ph.file_size)
            await message.bot.download(photo.file_id, path)
        except Exception:
            await message.answer("Произошла ошибка при загрузка фото, попробуйте еще раз")
            raise

        await state.update_data(has_image=message.text != "Пропустить")

        await message.answer("На данный момент функционал ограничен. Возвращайтесь позже")
        await state.clear()


@router.callback_query(F.data == "my_admins")
async def _my_admins(callback_query: CallbackQuery):
    uow_factory = get_app_uow_factory()
    async with uow_factory() as uow:
        answer = await menu_my_admins(uow, callback_query.from_user.id)
        await callback_query.message.edit_text(**answer)


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
async def _add_admin(callback_query: CallbackQuery, state: FSMContext):
    uow_factory = get_app_uow_factory()
    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(callback_query.from_user.id)
        if school_admin is None:
            await callback_query.message.edit_text("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        await callback_query.message.answer(
            "Отправьте пользователя (или несколько), которому будет выдано разрешение на администрирование",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="Выбрать пользователя(ей)",
                                          request_users=KeyboardButtonRequestUsers(
                                              request_id=0, user_is_bot=False, request_name=True, max_quantity=10))],
                          [KeyboardButton(text="Отмена", icon_custom_emoji_id="5210952531676504517")]],
                is_persistent=True, resize_keyboard=True, input_field_placeholder="Выберите кнопкой"))
        await state.set_state(AddMyAdminsStatesGroup.users_shared)
        await callback_query.message.delete()


@router.message(AddMyAdminsStatesGroup.users_shared)
async def _add_admin(message: Message):
    if message.content_type != ContentType.USERS_SHARED and message.text != "Отмена":
        await message.answer("Нажмите на кнопку, чтобы выбрать, или отмените операцию")
        return

    uow_factory = get_app_uow_factory()
    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(message.from_user.id)
        if school_admin is None:
            await message.answer("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        await (await message.answer(".", reply_markup=ReplyKeyboardRemove())).delete()

        if message.content_type == ContentType.USERS_SHARED:
            users = [(user.user_id, ' '.join([user.first_name, user.last_name or '']).strip()) for user in message.users_shared.users]
            my_admins = await uow.school_admin_repository.get_my_admins(message.from_user.id)

            if len(my_admins) + len(users) > MY_ADMINS_LIMIT:
                await message.answer(f"Превышен лимит администраторов ({MY_ADMINS_LIMIT})")
            else:
                await uow.school_admin_repository.add_my_admins(message.from_user.id, users)
                await uow.statistic_repository.add_statistic(message.from_user.id, StatName.addSchoolAdminFrom)

        answer = await menu_my_admins(uow, message.from_user.id)
        await message.answer(**answer)


@router.callback_query(F.data.startswith("delete_my_admin|"))
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
