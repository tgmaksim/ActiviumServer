import re
import shutil

from typing import Optional
from datetime import datetime, date, timezone, timedelta

from yarl import URL
from pathlib import Path

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramBadRequest
from aiogram.enums import ContentType, MessageEntityType

from ..utils.message_model import MessageModel
from aiogram.utils.formatting import Text, CustomEmoji, Bold

from src.dependencies.datetime import astimezone
from src.dependencies.uow import get_app_uow_factory
from src.models.school_admin_model import SchoolAdmin
from src.repositories.statistic_repository import StatName

from src.config.project_config import settings
from src.support.repositories.app_uow import AppUnitOfWork

from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    KeyboardButton,
    LinkPreviewOptions,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButtonRequestUsers,
)


__all__ = ['router']

router = Router()

uow_factory = get_app_uow_factory()

MY_ADMINS_LIMIT = 5  # Лимит дочерних администраторов образовательной организации
SHOWN_POSTS_LIMIT = 5  # Лимит постов в списке

POST_TITLE_LIMIT = 128  # Лимит длины заголовка поста
POST_DESCRIPTION_LIMIT = 256  # Лимит длины описания поста
POST_SUBTITLE_LIMIT = 64  # Лимит длины подзаголовка в содержании поста


class AddMyAdminsStatesGroup(StatesGroup):
    """Группа состояний при добавлении дочернего администратора образовательной организации"""

    users_shared = State('users_shared')
    """Ожидание сообщения с пользователями"""


class CreatePostStatesGroup(StatesGroup):
    """Группа состояний при создании поста"""

    title = State('title')
    """Ожидание сообщения с заголовком поста"""
    description = State('description')
    """Ожидание сообщения с описанием поста"""
    image = State('image')
    """Ожидание сообщения с главной картинкой поста"""
    show_schedule_date = State('show_schedule_date')
    """Ожидание сообщения с датой мероприятия для поста"""
    content = State('content')
    """Ожидание сообщения с содержанием поста"""


async def secure_edit_message(callback_query: CallbackQuery, **kwargs):
    """Изменить сообщения или в случе ошибки 'message is not modified' вызвать answer()"""

    try:
        await callback_query.message.edit_text(**kwargs)
    except TelegramBadRequest as e:
        if "message is not modified" in e.message:
            await callback_query.answer()
        else:
            raise


async def send_loading(message: Message, text: str):
    """Отправка сообщения с эмодзи загрузки"""

    return await message.answer(
        **Text(text, " ", CustomEmoji("🔵", custom_emoji_id="5235997383627658618")).as_kwargs()
    )


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


@router.callback_query(F.data == "admin_stats")
async def _admin_stats(callback_query: CallbackQuery):
    """Просмотр статистики по приложению в образовательной организации"""

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


@router.callback_query(F.data.startswith("school_posts|"))
async def _school_posts(callback_query: CallbackQuery):
    """Просмотр списка опубликованных постов"""

    offset = int(callback_query.data.split("|")[1])

    async with uow_factory() as uow:
        answer = await menu_school_posts(uow, callback_query.from_user.id, offset)

        await secure_edit_message(callback_query, **answer)


async def menu_school_posts(uow: AppUnitOfWork, user_id: int, offset: int) -> MessageModel:
    """Список школьных постов"""

    school_admin = await uow.school_admin_repository.get_admin(user_id)
    if school_admin is None:
        return MessageModel(text="Меню Активиум доступно только администраторам ОО\nДля подключения: /school")

    posts = await uow.school_post_repository.get_admin_school_posts(
        school_admin.dnevnik_admin.school_id,
        offset=offset,
        limit=SHOWN_POSTS_LIMIT + 1  # Для проверки существования следующего поста после лимита
    )

    right_offset = offset + SHOWN_POSTS_LIMIT
    left_offset = max(0, offset - SHOWN_POSTS_LIMIT)

    # Кнопки для открытия меню поста
    buttons = [[InlineKeyboardButton(
        text=post.title,
        callback_data=f"school_post|{post.post_id}|{offset}"
    )] for i, post in enumerate(posts) if i < SHOWN_POSTS_LIMIT]

    # Кнопки влево, обновить, вправо для перемещения по списку
    buttons.append([
        InlineKeyboardButton(text=" ", icon_custom_emoji_id="5877536313623711363" if left_offset != offset else None,
                             callback_data=f"school_posts|{left_offset}"),
        InlineKeyboardButton(text=" ", icon_custom_emoji_id="5030872266716480568",
                             callback_data=f"school_posts|{offset}"),
        InlineKeyboardButton(text=" ", icon_custom_emoji_id="5875506366050734240" if len(posts) > SHOWN_POSTS_LIMIT else None,
                             callback_data=f"school_posts|{right_offset}")
    ])

    buttons.append([InlineKeyboardButton(text="Создать публикацию", icon_custom_emoji_id="5397916757333654639", callback_data="create_post")])
    buttons.append([InlineKeyboardButton(text="Назад", icon_custom_emoji_id="5467864676320681402", callback_data="menu")])

    return MessageModel(
        text=Text(CustomEmoji("🎙", custom_emoji_id="5382013970905309819"), " Новости и мероприятия"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data.startswith("school_post|"))
async def _school_post(callback_query: CallbackQuery):
    """Меню поста"""

    post_id, offset = map(int, callback_query.data.split("|")[1:])

    async with uow_factory() as uow:
        answer = await menu_school_post(uow, callback_query.from_user.id, post_id, f"school_posts|{offset}")

        await secure_edit_message(callback_query, **answer)


async def menu_school_post(uow: AppUnitOfWork, user_id: int, post_id: int, callback: str) -> MessageModel:
    """Меню поста"""

    school_admin = await uow.school_admin_repository.get_admin(user_id)
    if school_admin is None:
        return MessageModel(text="Меню Активиум доступно только администраторам ОО\nДля подключения: /school")

    # Получение поста или открытие списка всех постов
    post = await uow.school_post_repository.get_post(post_id)
    if post is None:
        return await menu_school_posts(uow, user_id, 0)

    # Ссылка на главную картинку поста
    image_relative_path = ('school', 'posts', str(post_id), 'image.jpg')
    image_url = str(URL(settings.URL).joinpath(*image_relative_path))

    # Показ картинки через предпросмотр
    preview_options = LinkPreviewOptions(
        is_disabled=False,
        url=settings.TELEGRAM_PREVIEW_URL + image_url,  # Прокси для доступа Telegram к серверу
        prefer_large_media=True,
        show_above_text=True
    ) if post.has_image else None

    created_at = astimezone(post.created_at, school_admin.dnevnik_admin.timezone).strftime('%e %b. в %H:%M').strip()
    schedule_date = post.schedule_date.strftime('%e %b.').strip() if post.schedule_date is not None else 'нет'
    edited = 'да' if post.is_updated else 'нет'

    text = Text(
        Bold(post.title), "\n",
        post.description or "<Без описания>", "\n\n",
        "Публикация от ", created_at, "\n",
        "В расписании: ", schedule_date, "\n",
        "Отредактировано: ", edited, "\n",
        "Увидели: ", post.count_visions, "\n",
        "Открытия: ", post.count_clicks, "\n",
        "Просмотры: ", post.count_viewings, "\n",
        "Реакции: ", post.count_likes
    )

    # Ссылка на открытие поста (только для администраторов ОО)
    post_relative_path = ('school', 'posts', str(post_id))
    url = str(URL(settings.URL).joinpath(*post_relative_path))

    buttons = [
        [InlineKeyboardButton(text="Посмотреть", icon_custom_emoji_id="5210956306952758910", url=url),
         InlineKeyboardButton(text="Редактировать", icon_custom_emoji_id="5395444784611480792", callback_data=f"edit_post|{post_id}")],
        [InlineKeyboardButton(text="Удалить публикацию", icon_custom_emoji_id="5210952531676504517", callback_data=f"delete_post|{post_id}")],
        [InlineKeyboardButton(text="Назад", icon_custom_emoji_id="5467864676320681402", callback_data=callback)]
    ]

    return MessageModel(
        text=text,
        link_preview_options=preview_options,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data == "create_post")
async def _create_post(callback_query: CallbackQuery, state: FSMContext):
    """Создать новый пост"""

    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(callback_query.from_user.id)
        if school_admin is None:
            await callback_query.message.edit_text("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        # Временная директория для хранения файлов поста
        temp_post_relative_path = ('temp', 'school', 'posts', str(callback_query.from_user.id))
        temp_post_path = Path(settings.WWW_PATH, *temp_post_relative_path)
        temp_post_path.mkdir(parents=True, exist_ok=True)

        answer = wait_post_title()
        await callback_query.message.answer(**answer)

        await state.set_state(CreatePostStatesGroup.title)

        await callback_query.message.delete()


def wait_post_title() -> MessageModel:
    """Ожидание сообщения с заголовком поста"""

    return MessageModel(
        text=f"Вы начали создание поста\nОтправьте заголовок (от 1 до {POST_TITLE_LIMIT} символов)\n"
             "В любой момент нажмите на кнопку Отмена для сброса операции",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Отмена", icon_custom_emoji_id="5210952531676504517")]],
            resize_keyboard=True
        )
    )


async def cancel_create_post(uow: AppUnitOfWork, user_id: int, state: FSMContext) -> MessageModel:
    """Завершение создания поста"""

    await state.clear()

    # Удаление временных файлов
    temp_post_relative_path = ('temp', 'school', 'posts', str(user_id))
    temp_post_path = Path(settings.WWW_PATH, *temp_post_relative_path)
    shutil.rmtree(temp_post_path)

    return await menu_school_posts(uow, user_id, 0)


@router.message(CreatePostStatesGroup.title)
async def _post_title(message: Message, state: FSMContext):
    """Выбор заголовка нового поста"""

    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(message.from_user.id)
        if school_admin is None:
            await state.clear()
            await message.answer("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        if message.text == "Отмена":
            await (await message.answer(".", reply_markup=ReplyKeyboardRemove())).delete()

            answer = await cancel_create_post(uow, message.from_user.id, state)
            await message.answer(**answer)
            return

        if message.content_type != ContentType.TEXT:
            await message.answer("Отправьте заголовок статьи!")
            return

        if (len_text := len(message.text)) > POST_TITLE_LIMIT:
            await message.answer(f"Вы превысили лимит длины заголовка ({len_text})")
            return

        # Сохранение полученного заголовка
        await state.update_data(title=message.text)

        answer = wait_post_description()
        await message.answer(**answer)

        await state.set_state(CreatePostStatesGroup.description)


def wait_post_description() -> MessageModel:
    """Ожидание сообщения с описанием поста"""

    return MessageModel(
        text=f"Отлично! Теперь отправьте короткое описание (от 1 до {POST_DESCRIPTION_LIMIT} символов), "
             "которое будет сопровождать заголовок. Если оно не требуется, нажмите на кнопку Пропустить",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Пропустить", icon_custom_emoji_id="5416117059207572332")],
                [KeyboardButton(text="Прошлый шаг", icon_custom_emoji_id="5467864676320681402")],
                [KeyboardButton(text="Отмена", icon_custom_emoji_id="5210952531676504517")]
            ],
            resize_keyboard=True
        )
    )


@router.message(CreatePostStatesGroup.description)
async def _post_description(message: Message, state: FSMContext):
    """Выбор описания поста"""

    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(message.from_user.id)
        if school_admin is None:
            await state.clear()
            await message.answer("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        if message.text == "Отмена":
            await (await message.answer(".", reply_markup=ReplyKeyboardRemove())).delete()

            answer = await cancel_create_post(uow, message.from_user.id, state)
            await message.answer(**answer)
            return

        if message.text == "Прошлый шаг":
            answer = wait_post_title()
            await message.answer(**answer)

            await state.set_state(CreatePostStatesGroup.title)
            return

        if message.content_type != ContentType.TEXT:
            await message.answer("Отправьте описание статьи!")
            return

        if (len_text := len(message.text)) > POST_DESCRIPTION_LIMIT:
            await message.answer(f"Вы превысили лимит длины заголовка ({len_text})")
            return

        # Сохранение полученного описания
        await state.update_data(description=None if message.text == "Пропустить" else message.text)

        answer = wait_post_image()
        await message.answer(**answer)

        await state.set_state(CreatePostStatesGroup.image)


def wait_post_image() -> MessageModel:
    """Ожидание сообщения с главной картинкой поста"""

    return MessageModel(
        text="Продолжим. Отправьте главную фотографию статьи. Если она не требуется, нажмите на кнопку Пропустить",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Пропустить", icon_custom_emoji_id="5416117059207572332")],
                [KeyboardButton(text="Прошлый шаг", icon_custom_emoji_id="5467864676320681402")],
                [KeyboardButton(text="Отмена", icon_custom_emoji_id="5210952531676504517")]
            ],
            resize_keyboard=True
        )
    )


@router.message(CreatePostStatesGroup.image)
async def _post_image(message: Message, state: FSMContext):
    """Выбор главной картинки поста"""

    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(message.from_user.id)
        if school_admin is None:
            await state.clear()
            await message.answer("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        if message.text == "Отмена":
            await (await message.answer(".", reply_markup=ReplyKeyboardRemove())).delete()

            answer = await cancel_create_post(uow, message.from_user.id, state)
            await message.answer(**answer)
            return

        if message.text == "Прошлый шаг":
            answer = wait_post_description()
            await message.answer(**answer)

            await state.set_state(CreatePostStatesGroup.description)
            return

        if message.text != "Пропустить":
            if message.content_type != ContentType.PHOTO:
                await message.answer("Отправьте фото статьи!")
                return

            # Путь к файлу во временной директории
            image_relative_path = ('temp', 'school', 'posts', str(message.from_user.id), 'image.jpg')
            path = Path(settings.WWW_PATH, *image_relative_path)

            # Отправка сообщения с эмодзи загрузки, чтобы пользовать ожидал
            loading = await send_loading(message, "Фото загружается")

            try:
                photo = max(message.photo, key=lambda ph: ph.file_size)  # Самое лучшее качество
                await message.bot.download(photo.file_id, path)  # Скачивание фотографии
            except Exception:
                await message.answer("Произошла ошибка при загрузке фото, попробуйте еще раз")
                raise
            finally:
                await loading.delete()

        # Сохранение информации о наличии главной картинки
        await state.update_data(has_image=message.text != "Пропустить")

        answer = wait_schedule_date()
        await message.answer(**answer)

        await state.set_state(CreatePostStatesGroup.show_schedule_date)


def wait_schedule_date() -> MessageModel:
    """Ожидание сообщения с датой мероприятия"""

    return MessageModel(
        text="Предпоследнее. Вы можете выбрать дату события, тогда в расписании после списка уроков будет "
             "располагаться данная публикация. Отправьте дату в формате ДД.ММ.ГГГГ или введите любой текст, выделите "
             "его и там же, где можно сделать текст жирным, выберите дату (в самом низу списка). Если дата не "
             "требуется, нажмите на кнопку Пропустить",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Пропустить", icon_custom_emoji_id="5416117059207572332")],
                [KeyboardButton(text="Прошлый шаг", icon_custom_emoji_id="5467864676320681402")],
                [KeyboardButton(text="Отмена", icon_custom_emoji_id="5210952531676504517")]
            ],
            resize_keyboard=True
        )
    )


@router.message(CreatePostStatesGroup.show_schedule_date)
async def _post_schedule_date(message: Message, state: FSMContext):
    """Выбор даты мероприятия"""

    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(message.from_user.id)
        if school_admin is None:
            await state.clear()
            await message.answer("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        if message.text == "Отмена":
            await (await message.answer(".", reply_markup=ReplyKeyboardRemove())).delete()

            answer = await cancel_create_post(uow, message.from_user.id, state)
            await message.answer(**answer)
            return

        if message.text == "Прошлый шаг":
            # Удаление загруженной картинки с прошлого шага
            temp_image_relative_path = ('temp', 'school', 'posts', str(message.from_user.id), 'image.jpg')
            temp_image_path = Path(settings.WWW_PATH, *temp_image_relative_path)
            temp_image_path.unlink(missing_ok=True)

            answer = wait_post_image()
            await message.answer(**answer)

            await state.set_state(CreatePostStatesGroup.image)
            return

        if message.content_type != ContentType.TEXT:
            await message.answer("Отправьте дату в текстовом формате!")
            return

        schedule_date: Optional[date] = None

        # Получение даты из текста сообщения или форматирования
        if message.text != "Пропустить":
            for entity in (message.entities or []):
                if entity.type == MessageEntityType.DATE_TIME:
                    tz = timezone(offset=timedelta(seconds=school_admin.dnevnik_admin.timezone))  # Часовой пояс администратора
                    schedule_date = datetime.fromtimestamp(entity.unix_time, tz).date()  # Нужна только дата
                    break

            # В качестве разделителя чисел может быть любой символ, а год указан как полностью (2026), так и коротко (26)
            date_pattern = r'(?P<day>\d{1,2}).(?P<month>\d{1,2}).(?P<year>(\d{2}){1,2})'

            # Если в форматировании даты нет, то используется текст сообщения в определенном формате
            if schedule_date is None and (match := re.match(date_pattern, message.text)):
                data = match.groupdict()

                year = data['year']
                if len(year) == 2:
                    year = f"20{year}"

                schedule_date = date(day=int(data['day']), month=int(data['month']), year=int(year))

            if schedule_date is None:
                await message.answer("Дата не найдена!")
                return

        # Сохранение даты мероприятия
        await state.update_data(schedule_date=schedule_date and schedule_date.isoformat(), offset=0)

        await message.answer(
            "Наконец-то можно писать. Теперь отправляйте содержание публикации: текст "
            "(каждый абзац отдельным сообщением), фото и видео (до 20МБ). В тексте можете использовать форматирование "
            "(жирный, курсив и др.). Чтобы написать подзаголовок в тексте, отправьте его полностью с жирным "
            "форматированием (выделите текст и выберите жирный в меню Telegram). "
            "Вы также можете отправить медиа и текст вместе для добавления подписи",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Прошлый шаг", icon_custom_emoji_id="5467864676320681402")],
                    [KeyboardButton(text="Отмена", icon_custom_emoji_id="5210952531676504517")]
                ],
                resize_keyboard=True
            )
        )

        await state.set_state(CreatePostStatesGroup.content)


@router.message(CreatePostStatesGroup.content)
async def _post_content(message: Message, state: FSMContext):
    """Последовательное написание поста по абзацам"""

    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(message.from_user.id)
        if school_admin is None:
            await state.clear()
            await message.answer("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        if message.text == "Отмена":
            await (await message.answer(".", reply_markup=ReplyKeyboardRemove())).delete()

            answer = await cancel_create_post(uow, message.from_user.id, state)
            await message.answer(**answer)
            return

        if message.text == "Опубликовать":
            data = await state.get_data()
            post_id = await create_post(uow, school_admin, data)
            await state.clear()

            await (await message.answer(".", reply_markup=ReplyKeyboardRemove())).delete()

            answer = await menu_school_post(uow, message.from_user.id, post_id, 'school_posts|0')
            await message.answer(**answer)
            return

        offset: int = (await state.get_data())['offset']
        old_offset = offset - 1
        new_offset = offset + 1
        last_content_key = f'content|{old_offset}'
        next_content_key = f'content|{offset}'

        if message.text == "Прошлый шаг":
            # Директория с временными файлами поста
            temp_media_relative_path = ('temp', 'school', 'posts', str(message.from_user.id))
            temp_media_path = Path(settings.WWW_PATH, *temp_media_relative_path)

            # Поиск файла с названием <offset>.ext и его удаление
            for file in temp_media_path.iterdir():
                if file.is_file() and file.stem == str(offset):
                    file.unlink(missing_ok=True)
                    break

            # Если это первый абзац, то прошлым шагом было добавление даты мероприятия
            if offset == 0:
                answer = wait_schedule_date()
                await message.answer(**answer)

                await state.set_state(CreatePostStatesGroup.show_schedule_date)
            else:
                # Удаление прошлого абзаца
                await state.update_data({last_content_key: None}, offset=old_offset)

                await message.answer("Прошлая часть поста была удалена. Вы можете написать ее снова")

            return

        # Добавление поддерживаемого форматирования
        entities = []
        for entity in (message.entities or message.caption_entities or []):
            if entity.type in (
                    MessageEntityType.URL, MessageEntityType.BOLD, MessageEntityType.ITALIC,
                    MessageEntityType.UNDERLINE, MessageEntityType.STRIKETHROUGH, MessageEntityType.BLOCKQUOTE,
                    MessageEntityType.EXPANDABLE_BLOCKQUOTE
            ):
                entities.append({'type': entity.type, 'offset': entity.offset, 'length': entity.length})
            elif entity.type == MessageEntityType.TEXT_LINK:
                entities.append({'type': entity.type, 'offset': entity.offset, 'length': entity.length, 'url': entity.url})

        # Заголовок (текст полностью жирный)
        if (message.content_type == ContentType.TEXT and len(message.entities or []) == 1 and
                (entity := message.entities[0]).type == MessageEntityType.BOLD and entity.offset == 0 and
                entity.length == len(message.text)):
            if len(message.text) > POST_SUBTITLE_LIMIT:
                await message.answer(f"Заголовок превысил лимит ({POST_SUBTITLE_LIMIT} символов) длины")
                return

            # Добавление заголовка в содержание
            await state.update_data({
                next_content_key: {
                    'type': 'title',
                    'text': message.text,
                    'entities': []
                }
            }, offset=new_offset)

        # Обычный абзац
        elif message.content_type == ContentType.TEXT:
            await state.update_data({
                next_content_key: {
                    'type': 'text',
                    'text': message.text,
                    'entities': entities
                }
            }, offset=new_offset)

        # Медиа (фото или видео)
        elif message.content_type in (ContentType.PHOTO, ContentType.VIDEO, ContentType.VIDEO_NOTE, ContentType.ANIMATION):
            ext = 'jpg' if message.content_type == ContentType.PHOTO else 'mp4'
            media_relative_path = ('temp', 'school', 'posts', str(message.from_user.id), f'{offset}.{ext}')
            path = Path(settings.WWW_PATH, *media_relative_path)

            # Отправка сообщения с эмодзи загрузки, чтобы пользовать ожидал
            loading = await send_loading(message, "Медиа загружается")

            if message.content_type == ContentType.PHOTO:
                media = max(message.photo, key=lambda ph: ph.file_size)  # Самое лучшее качество
            else:
                media = message.video or message.video_note or message.animation

            try:
                await message.bot.download(media.file_id, path)  # Скачивание медиа
            except Exception:
                await message.answer("Произошла ошибка при загрузке медиа, попробуйте еще раз")
                raise
            finally:
                await loading.delete()

            # Сохранение информации о медиа в содержании
            await state.update_data({
                next_content_key: {
                    'type': 'photo' if message.content_type == ContentType.PHOTO else 'video',
                    'text': message.caption,
                    'entities': entities,
                    **({} if message.content_type == ContentType.PHOTO
                       else {'round': message.content_type == ContentType.VIDEO_NOTE})
                }
            }, offset=new_offset)

        else:
            await message.answer("Неподдерживаемый тип медиа")
            return

        await message.answer(
            "Обработано! Продолжайте писать статью",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Прошлый шаг", icon_custom_emoji_id="5467864676320681402")],
                    [KeyboardButton(text="Опубликовать", icon_custom_emoji_id="5406575351272872039")],
                    [KeyboardButton(text="Отмена", icon_custom_emoji_id="5210952531676504517")]
                ],
                resize_keyboard=True
            )
        )


async def create_post(uow: AppUnitOfWork, school_admin: SchoolAdmin, data: dict) -> int:
    """
    Создание поста

    :param uow: AppUnitOfWork для взаимодействия с БД
    :param school_admin: администратор образовательной организации
    :param data: данные поста (заголовок, картинка, содержание и др.)
    :return: идентификатор созданного поста
    """

    # Сбор содержания поста
    _content: dict[int, dict] = {}
    for key, value in data.items():
        if value is None:
            continue
        if key.startswith('content'):
            index = int(key.split('|')[1])
            _content[index] = value

    # Из словаря в список
    content = list(map(lambda c: c[1], sorted(_content.items(), key=lambda c: c[0])))

    # Создание поста со всеми параметрами
    post = await uow.school_post_repository.create_post(
        school_admin.dnevnik_admin.school_id,
        school_admin.dnevnik_admin.timezone,
        title=data['title'],
        description=data['description'],
        has_image=data['has_image'],
        author=school_admin.name,
        schedule_date=(schedule_date := data['schedule_date']) and date.fromisoformat(schedule_date),
        content=content
    )

    # Временная директория и постоянная для хранения файлов поста
    temp_media_relative_path = ('temp', 'school', 'posts', str(school_admin.user_id))
    temp_media_path = Path(settings.WWW_PATH, *temp_media_relative_path)
    media_relative_path = ('school', 'posts', str(post.post_id))
    media_path = Path(settings.WWW_PATH, *media_relative_path)

    temp_media_path.replace(media_path)

    return post.post_id


@router.callback_query(F.data.startswith("delete_post|"))
async def _delete_post(callback_query: CallbackQuery):
    """Удалить пост"""

    post_id = int(callback_query.data.split("|")[1])

    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(callback_query.from_user.id)
        if school_admin is None:
            await callback_query.message.edit_text("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        # Удаление всех файлов поста
        media_relative_path = ('school', 'posts', str(post_id))
        media_path = Path(settings.WWW_PATH, *media_relative_path)
        shutil.rmtree(media_path)

        await uow.school_post_repository.delete_post(post_id)

        answer = await menu_school_posts(uow, callback_query.from_user.id, 0)
        await callback_query.message.edit_text(**answer)


@router.callback_query(F.data.startswith("edit_post|"))
async def _edit_post(callback_query: CallbackQuery):
    """Редактирования поста"""

    post_id = int(callback_query.data.split("|")[1])

    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(callback_query.from_user.id)
        if school_admin is None:
            await callback_query.message.edit_text("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        await callback_query.answer("Данный функционал еще в разработке!", show_alert=True)


@router.callback_query(F.data == "my_admins")
async def _my_admins(callback_query: CallbackQuery):
    """Список дочерних администраторов образовательной организации"""

    async with uow_factory() as uow:
        answer = await menu_my_admins(uow, callback_query.from_user.id)
        await callback_query.message.edit_text(**answer)


async def menu_my_admins(uow: AppUnitOfWork, user_id: int) -> MessageModel:
    """Список дочерних администраторов образовательной организации"""

    school_admin = await uow.school_admin_repository.get_admin(user_id)
    if school_admin is None:
        return MessageModel(text="Меню Активиум доступно только администраторам ОО\nДля подключения: /school")

    # Дочерние администраторы образовательной организации
    my_admins = await uow.school_admin_repository.get_my_admins(user_id)

    # Кнопки для удаления дочерних администраторов образовательной организации
    buttons = [[InlineKeyboardButton(
        text=admin.name,
        icon_custom_emoji_id="5210952531676504517",
        callback_data=f"delete_my_admin|{admin.user_id}"
    )] for admin in my_admins]

    buttons.append([InlineKeyboardButton(text="Добавить администратора", icon_custom_emoji_id="5397916757333654639", callback_data="add_admin")])
    buttons.append([InlineKeyboardButton(text="Назад", icon_custom_emoji_id="5467864676320681402", callback_data="menu")])

    return MessageModel(
        text=Text(CustomEmoji("✅", custom_emoji_id="5440712623219822019"), " Мои администраторы"),
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons)
    )


@router.callback_query(F.data == "add_admin")
async def _query_add_admin(callback_query: CallbackQuery, state: FSMContext):
    """Добавление дочернего администратора образовательной организации"""

    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(callback_query.from_user.id)
        if school_admin is None:
            await callback_query.message.edit_text("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        await callback_query.message.answer(
            "Отправьте пользователя (или несколько), которому будет выдано разрешение на администрирование",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Выбрать пользователя(ей)", request_users=KeyboardButtonRequestUsers(
                        request_id=0, user_is_bot=False, request_name=True, max_quantity=10))],
                    [KeyboardButton(text="Отмена", icon_custom_emoji_id="5210952531676504517")]
                ],
                is_persistent=True, resize_keyboard=True, input_field_placeholder="Выберите кнопкой")
        )
        await callback_query.message.delete()

        await state.set_state(AddMyAdminsStatesGroup.users_shared)


@router.message(AddMyAdminsStatesGroup.users_shared)
async def _add_admin(message: Message, state: FSMContext):
    """Ожидание сообщения с администратором(ами) образовательной организации"""

    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(message.from_user.id)
        if school_admin is None:
            await message.answer("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        if message.content_type != ContentType.USERS_SHARED and message.text != "Отмена":
            await message.answer("Пришлите администратором кнопкой")
            return

        await (await message.answer(".", reply_markup=ReplyKeyboardRemove())).delete()

        if message.content_type == ContentType.USERS_SHARED:
            users = [(
                user.user_id,
                ' '.join([user.first_name, user.last_name or '']).strip()
            ) for user in message.users_shared.users]
            my_admins = await uow.school_admin_repository.get_my_admins(message.from_user.id)

            if len(my_admins) + len(users) > MY_ADMINS_LIMIT:
                await message.answer(f"Превышен лимит администраторов ({MY_ADMINS_LIMIT})")
            else:
                await uow.school_admin_repository.add_my_admins(message.from_user.id, users)

                await uow.statistic_repository.add_statistic(message.from_user.id, StatName.addSchoolAdminFrom)

        answer = await menu_my_admins(uow, message.from_user.id)
        await message.answer(**answer)

        await state.clear()


@router.callback_query(F.data.startswith("delete_my_admin|"))
async def _delete_admin(callback_query: CallbackQuery):
    """Удаление дочернего администратора образовательной организации"""

    admin_id = int(callback_query.data.split("|")[1])

    async with uow_factory() as uow:
        school_admin = await uow.school_admin_repository.get_admin(callback_query.from_user.id)
        if school_admin is None:
            await callback_query.answer("Меню Активиум доступно только администраторам ОО\nДля подключения: /school")
            return

        await uow.school_admin_repository.delete_my_admin(callback_query.from_user.id, admin_id)

        await uow.statistic_repository.add_statistic(callback_query.from_user.id, StatName.deleteSchoolAdminFrom)

        answer = await menu_my_admins(uow, callback_query.from_user.id)
        await callback_query.message.edit_text(**answer)
