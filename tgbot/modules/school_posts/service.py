import re
import shutil

from src.utils.datetime import astimezone
from datetime import date, timezone, timedelta, datetime

from yarl import URL
from pathlib import Path
from typing import Optional, Any

from aiogram.enums import MessageEntityType
from aiogram.types import LinkPreviewOptions, MessageEntity

from ...enums.emoji import EmojiList
from aiogram.utils.formatting import Text, Bold
from ...schemas.service_result import ServiceResult
from .constants import SHOWN_POSTS_LIMIT, POST_TITLE_LIMIT, POST_DESCRIPTION_LIMIT
from .buttons import posts_buttons, post_buttons, back_button, optional_stage_buttons

from src.models import SchoolAdmin
from src.config.project_config import settings
from src.services.base_service import BaseService
from src.support.repositories.app_uow import AppUnitOfWork


__all__ = ['SchoolPostsService']


class SchoolPostsService(BaseService[AppUnitOfWork]):
    """Сервис для работы со школьными публикациями"""

    async def school_posts(self, school_admin: SchoolAdmin, offset: Optional[int]) -> ServiceResult:
        if offset is None:
            offset = 0

        async with self.uow_factory() as uow:
            posts = await uow.school_post_repository.get_admin_school_posts(
                school_admin.dnevnik_admin.school_id,
                offset=offset,
                limit=SHOWN_POSTS_LIMIT + 1  # Для проверки существования следующего поста после лимита
            )

        right_offset = offset + SHOWN_POSTS_LIMIT if len(posts) > SHOWN_POSTS_LIMIT else offset
        left_offset = max(0, offset - SHOWN_POSTS_LIMIT)

        text = Text(
            EmojiList.microphone.value, "Новости и мероприятия"
        )

        reply_markup = posts_buttons(
            [(post.post_id, post.title) for post in posts[:SHOWN_POSTS_LIMIT]],
            offset, left_offset, right_offset
        )

        return ServiceResult(text=text, reply_markup=reply_markup)

    async def school_post(self, school_admin: SchoolAdmin, post_id: int, offset: Optional[int]) -> ServiceResult:
        async with self.uow_factory() as uow:
            post = await uow.school_post_repository.get_post(post_id)

        if post is None:
            return await self.school_posts(school_admin, offset)

        # Ссылка на главную картинку поста
        image_relative_path = ('school', 'posts', str(post_id), 'image.jpg')
        image_url = str(URL(settings.URL_FOR_TG).joinpath(*image_relative_path))

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
        url = str(URL(settings.URL_FOR_TG).joinpath(*post_relative_path))

        reply_markup = post_buttons(url, post_id, offset)

        return ServiceResult(text=text, reply_markup=reply_markup, link_preview_options=preview_options)

    @classmethod
    def stage_info(cls, user_id: int) -> ServiceResult:
        # Временная директория для хранения файлов поста
        temp_post_relative_path = ('temp', 'school', 'posts', str(user_id))
        temp_post_path = Path(settings.WWW_PATH, *temp_post_relative_path)
        temp_post_path.mkdir(parents=True, exist_ok=True)

        return cls.wait_title()

    @classmethod
    def wait_title(cls) -> ServiceResult:
        text = Text(
            f"Вы начали создание поста\nОтправьте заголовок (от 1 до {POST_TITLE_LIMIT} символов)\n"
            "В любой момент нажмите на кнопку Отмена для сброса операции"
        )
        reply_markup = back_button()

        return ServiceResult(text=text, reply_markup=reply_markup)

    @classmethod
    def stage_title(cls, text: str) -> ServiceResult:
        if (len_text := len(text)) > POST_TITLE_LIMIT:
            text = Text(
                f"Вы превысили лимит длины заголовка ({len_text})"
            )
            return ServiceResult(success=False, text=text)

        return cls.wait_description()

    @classmethod
    def wait_description(cls) -> ServiceResult:
        text = Text(
            f"Отлично! Теперь отправьте короткое описание (от 1 до {POST_DESCRIPTION_LIMIT} символов), "
            "которое будет сопровождать заголовок. Если оно не требуется, нажмите на кнопку Пропустить"
        )
        reply_markup = optional_stage_buttons()

        return ServiceResult(text=text, reply_markup=reply_markup)

    @classmethod
    def stage_description(cls, text: str) -> ServiceResult:
        if (len_text := len(text)) > POST_DESCRIPTION_LIMIT:
            text = Text(
                f"Вы превысили лимит длины описания ({len_text})"
            )
            return ServiceResult(success=False, text=text)

        return cls.wait_image()

    @classmethod
    def wait_image(cls) -> ServiceResult:
        text = Text(
            "Продолжим. Отправьте главную фотографию статьи. Если она не требуется, нажмите на кнопку Пропустить"
        )
        reply_markup = optional_stage_buttons()

        return ServiceResult(text=text, reply_markup=reply_markup)

    @classmethod
    def wait_schedule_date(cls) -> ServiceResult:
        text = Text(
            "Предпоследнее. Вы можете выбрать дату события, тогда в расписании после списка уроков будет "
            "располагаться данная публикация. Отправьте дату в формате ДД.ММ.ГГГГ или введите любой текст, выделите "
            "его и там же, где можно сделать текст жирным, выберите дату (в самом низу списка). Если дата не "
            "требуется, нажмите на кнопку Пропустить"
        )
        reply_markup = optional_stage_buttons()

        return ServiceResult(text=text, reply_markup=reply_markup)

    @classmethod
    def back_stage_image(cls, user_id: int) -> ServiceResult:
        # Удаление загруженной картинки с прошлого шага
        temp_image_relative_path = ('temp', 'school', 'posts', str(user_id), 'image.jpg')
        temp_image_path = Path(settings.WWW_PATH, *temp_image_relative_path)
        temp_image_path.unlink(missing_ok=True)

        return cls.wait_image()

    @classmethod
    def processing_schedule_date(cls, school_admin: SchoolAdmin, text: str, entities: list[MessageEntity]) -> Optional[date]:
        schedule_date: Optional[date] = None

        # Получение даты из текста сообщения или форматирования
        for entity in entities:
            if entity.type == MessageEntityType.DATE_TIME:
                tz = timezone(offset=timedelta(seconds=school_admin.dnevnik_admin.timezone))  # Часовой пояс администратора
                schedule_date = datetime.fromtimestamp(entity.unix_time, tz).date()  # Нужна только дата
                break

        # В качестве разделителя чисел может быть любой символ, а год указан как полностью (2026), так и коротко (26)
        date_pattern = r'(?P<day>\d{1,2}).(?P<month>\d{1,2}).(?P<year>(\d{2}){1,2})'

        # Если в форматировании даты нет, то используется текст сообщения в определенном формате
        if schedule_date is None and (match := re.match(date_pattern, text)):
            data = match.groupdict()

            year = data['year']
            if len(year) == 2:
                year = f"20{year}"

            schedule_date = date(day=int(data['day']), month=int(data['month']), year=int(year))

        return schedule_date

    @classmethod
    def back_from_stage_content(cls, user_id: int, offset: int) -> ServiceResult:
        # Директория с временными файлами поста
        temp_media_relative_path = ('temp', 'school', 'posts', str(user_id))
        temp_media_path = Path(settings.WWW_PATH, *temp_media_relative_path)

        # Поиск файла с названием <offset>.ext и его удаление
        for file in temp_media_path.iterdir():
            if file.is_file() and file.stem == str(offset):
                file.unlink(missing_ok=True)
                break

        # Если это первый абзац, то прошлым шагом было добавление даты мероприятия
        if offset == 0:
            return cls.wait_schedule_date()
        else:
            text = Text(
                "Прошлая часть поста была удалена. Вы можете написать ее снова"
            )
            return ServiceResult(text=text)

    async def cancel_create_post(self, school_admin: SchoolAdmin) -> ServiceResult:
        # Удаление временных файлов
        temp_post_relative_path = ('temp', 'school', 'posts', str(school_admin.user_id))
        temp_post_path = Path(settings.WWW_PATH, *temp_post_relative_path)
        shutil.rmtree(temp_post_path)

        answer = await self.school_posts(school_admin, offset=None)
        answer.service_params.delete_keyboard = True
        return answer

    async def create_post(self, school_admin: SchoolAdmin, data: dict[str, Any]) -> ServiceResult:
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

        async with self.uow_factory() as uow:
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

        answer = await self.school_post(school_admin, post.post_id, offset=None)
        answer.service_params.delete_keyboard = True

        return answer

    async def delete_post(self, school_admin: SchoolAdmin, post_id: int) -> ServiceResult:
        # Удаление всех файлов поста
        media_relative_path = ('school', 'posts', str(post_id))
        media_path = Path(settings.WWW_PATH, *media_relative_path)
        shutil.rmtree(media_path)

        async with self.uow_factory() as uow:
            await uow.school_post_repository.delete_post(post_id)

        return await self.school_posts(school_admin, offset=None)
