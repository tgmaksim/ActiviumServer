from pathlib import Path
from datetime import date
from typing import Optional

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter
from aiogram.enums import ContentType, MessageEntityType
from aiogram.types import Message, CallbackQuery, MessageEntity

from .utils import send_loading
from .service import SchoolPostsService
from aiogram.utils.formatting import Text
from .states import CreatePostStatesGroup
from .constants import POST_SUBTITLE_LIMIT
from .buttons import stage_buttons, stage_content_buttons

from src.config.project_config import settings
from src.models.school_admin_model import SchoolAdmin

from ...enums.modules import ModuleList
from ...utils.messages import send_service_result
from ...dependencies.services import ModuleService
from ...callbacks.school_posts import CallbackSchoolPosts


__all__ = ['router']

router = Router(name=ModuleList.school_posts)


@router.callback_query(CallbackSchoolPosts.filter_action('menu'), ModuleService(SchoolPostsService), flags={'auth': True})
async def _school_posts(callback_query: CallbackQuery, callback_data: CallbackSchoolPosts, service: SchoolPostsService, school_admin: SchoolAdmin):
    """Просмотр списка опубликованных постов"""

    answer = await service.school_posts(school_admin, callback_data.offset)
    await send_service_result(callback_query, answer)


@router.callback_query(CallbackSchoolPosts.filter_action('post'), ModuleService(SchoolPostsService), flags={'auth': True})
async def _school_post(callback_query: CallbackQuery, callback_data: CallbackSchoolPosts, service: SchoolPostsService, school_admin: SchoolAdmin):
    """Меню поста"""

    answer = await service.school_post(school_admin, callback_data.post_id, callback_data.offset)
    await send_service_result(callback_query, answer)


@router.callback_query(CallbackSchoolPosts.filter_action('create'), ModuleService(SchoolPostsService), flags={'full_auth': True})
async def _state_info(callback_query: CallbackQuery, state: FSMContext, service: SchoolPostsService):
    """Создать новый пост"""

    answer = service.stage_info(callback_query.from_user.id)
    answer.service_params.delete_message = True
    await send_service_result(callback_query, answer)

    await state.set_state(CreatePostStatesGroup.title)


@router.message(StateFilter(CreatePostStatesGroup), F.text == "Отмена", ModuleService(SchoolPostsService), flags={'auth': True})
async def _cancel_create_post(message: Message, state: FSMContext, service: SchoolPostsService, school_admin: SchoolAdmin):
    """Отмена создания поста на любом этапе"""

    await state.clear()

    answer = await service.cancel_create_post(school_admin)
    await send_service_result(message, answer)


@router.message(CreatePostStatesGroup.title, ModuleService(SchoolPostsService), flags={'auth': True})
async def _stage_title(message: Message, state: FSMContext, service: SchoolPostsService):
    """Выбор заголовка нового поста"""

    if message.content_type != ContentType.TEXT:
        await message.answer("Отправьте заголовок статьи!")
        return

    answer = service.stage_title(message.text)
    await send_service_result(message, answer)

    if answer.success:
        await state.update_data(title=message.text)
        await state.set_state(CreatePostStatesGroup.description)


@router.message(CreatePostStatesGroup.description, ModuleService(SchoolPostsService), flags={'auth': True})
async def _stage_description(message: Message, state: FSMContext, service: SchoolPostsService):
    """Выбор описания поста"""

    if message.text == "Прошлый шаг":
        answer = service.wait_title()
        await send_service_result(message, answer)

        await state.set_state(CreatePostStatesGroup.title)
        return

    if message.content_type != ContentType.TEXT:
        await message.answer("Отправьте описание статьи!")
        return

    answer = service.stage_description(message.text)
    await send_service_result(message, answer)

    if answer.success:
        await state.update_data(description=None if message.text == "Пропустить" else message.text)
        await state.set_state(CreatePostStatesGroup.image)


@router.message(CreatePostStatesGroup.image, ModuleService(SchoolPostsService), flags={'auth': True})
async def _stage_image(message: Message, state: FSMContext, service: SchoolPostsService):
    """Выбор главной картинки поста"""

    if message.text == "Прошлый шаг":
        answer = service.wait_description()
        await send_service_result(message, answer)

        await state.set_state(CreatePostStatesGroup.description)
        return

    if message.text != "Пропустить":
        if message.content_type != ContentType.PHOTO:
            await message.answer("Отправьте фото статьи!")
            return

        await download_post_image(message)

    answer = service.wait_schedule_date()
    await message.answer(**answer)

    await state.update_data(has_image=message.text != "Пропустить")
    await state.set_state(CreatePostStatesGroup.show_schedule_date)


async def download_post_image(message: Message):
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


@router.message(CreatePostStatesGroup.show_schedule_date, ModuleService(SchoolPostsService), flags={'auth': True})
async def _stage_schedule_date(message: Message, state: FSMContext, service: SchoolPostsService, school_admin: SchoolAdmin):
    """Выбор даты мероприятия"""

    if message.text == "Прошлый шаг":
        answer = service.back_stage_image(message.from_user.id)
        await send_service_result(message, answer)

        await state.set_state(CreatePostStatesGroup.image)
        return

    if message.content_type != ContentType.TEXT:
        await message.answer("Отправьте дату в текстовом формате!")
        return

    # Получение даты из текста сообщения или форматирования
    schedule_date: Optional[date] = None
    if message.text != "Пропустить":
        schedule_date = service.processing_schedule_date(school_admin, message.text, message.entities or [])

    text = Text(
        "Наконец-то можно писать. Теперь отправляйте содержание публикации: текст "
        "(каждый абзац отдельным сообщением), фото и видео (до 20МБ). В тексте можете использовать форматирование "
        "(жирный, курсив и др.). Чтобы написать подзаголовок в тексте, отправьте его полностью с жирным "
        "форматированием (выделите текст и выберите жирный в меню Telegram). "
        "Вы также можете отправить медиа и текст вместе для добавления подписи"
    )
    reply_markup = stage_buttons()

    await message.answer(**text.as_kwargs(), reply_markup=reply_markup)

    await state.update_data(schedule_date=schedule_date and schedule_date.isoformat(), offset=0)
    await state.set_state(CreatePostStatesGroup.content)


@router.message(CreatePostStatesGroup.content, F.text == "Опубликовать", ModuleService(SchoolPostsService), flags={'full_auth': True})
async def _create_post(message: Message, state: FSMContext, service: SchoolPostsService, school_admin: SchoolAdmin):
    """Публикация поста"""

    data = await state.get_data()
    await state.clear()

    answer = await service.create_post(school_admin, data)
    await send_service_result(message, answer)


@router.message(CreatePostStatesGroup.content, ModuleService(SchoolPostsService), flags={'auth': True})
async def _stage_content(message: Message, state: FSMContext, service: SchoolPostsService):
    """Последовательное написание поста по абзацам"""

    offset: int = (await state.get_data())['offset']
    new_offset = offset + 1
    next_content_key = f'content|{offset}'

    if message.text == "Прошлый шаг":
        answer = service.back_from_stage_content(message.from_user.id, offset)
        await send_service_result(message, answer)

        # Если это первый абзац, то прошлым шагом было добавление даты мероприятия
        if offset == 0:
            await state.set_state(CreatePostStatesGroup.show_schedule_date)
        else:
            old_offset = offset - 1
            last_content_key = f'content|{old_offset}'

            # Удаление прошлого абзаца
            await state.update_data({last_content_key: None}, offset=old_offset)

        return

    # Добавление поддерживаемого форматирования
    entities = processing_entities(message.entities or message.caption_entities or [])

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
        await download_content_media(message, offset)

        # Сохранение информации о медиа в содержании
        await state.update_data({
            next_content_key: {
                'type': 'photo' if message.content_type == ContentType.PHOTO else 'video',
                'text': message.caption,
                'entities': entities,
                **(
                    {} if message.content_type == ContentType.PHOTO
                    else {'round': message.content_type == ContentType.VIDEO_NOTE}
                )
            }
        }, offset=new_offset)

    else:
        await message.answer("Неподдерживаемый тип медиа")
        return

    text = Text(
        "Обработано! Продолжайте писать статью"
    )
    reply_markup = stage_content_buttons()

    await message.answer(**text.as_kwargs(), reply_markup=reply_markup)


def processing_entities(message_entities: list[MessageEntity]) -> list[dict]:
    entities = []

    for entity in message_entities:
        if entity.type in (
            MessageEntityType.URL, MessageEntityType.BOLD, MessageEntityType.ITALIC,
            MessageEntityType.UNDERLINE, MessageEntityType.STRIKETHROUGH, MessageEntityType.BLOCKQUOTE,
            MessageEntityType.EXPANDABLE_BLOCKQUOTE
        ):
            entities.append({'type': entity.type, 'offset': entity.offset, 'length': entity.length})
        elif entity.type == MessageEntityType.TEXT_LINK:
            entities.append({'type': entity.type, 'offset': entity.offset, 'length': entity.length, 'url': entity.url})

    return entities


async def download_content_media(message: Message, offset: int):
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


@router.callback_query(CallbackSchoolPosts.filter_action('delete'), ModuleService(SchoolPostsService), flags={'full_auth': True})
async def _delete_post(callback_query: CallbackQuery, callback_data: CallbackSchoolPosts, service: SchoolPostsService, school_admin: SchoolAdmin):
    """Удалить пост"""

    answer = await service.delete_post(school_admin, callback_data.post_id)
    await send_service_result(callback_query, answer)


@router.callback_query(CallbackSchoolPosts.filter_action('edit'), ModuleService(SchoolPostsService), flags={'full_auth': True})
async def _edit_post(callback_query: CallbackQuery):
    """Редактирования поста"""

    await callback_query.answer(
        "Данный функционал еще в разработке! Для изменения публикации обратитесь в поддержку",
        show_alert=True
    )
