from yarl import URL

from aiogram import Router

from aiogram.filters import Command
from aiogram.utils.formatting import Text, CustomEmoji, ExpandableBlockQuote
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CopyTextButton

from dnevnikru import AioDnevnikruApi

from src.config.project_config import settings


__all__ = ['router']

router = Router()


@router.message(Command('school'))
async def _cmd_school(message: Message):
    """Помощь в прохождении авторизации администратора образовательной организации"""

    # Ссылка для отправки сообщения другому пользователю
    share_url = ("tg://msg_url?text=Здравствуйте,+пройдите+авторизацию+в+Активиум,+чтобы+мы+могли+публиковать+новости+"
                 "и+мероприятия&url=t.me/ActiviumAppBot?start=school_auth")

    # Ссылка для прохождения авторизации администратора образовательной организации через Дневник.ру
    login_url = AioDnevnikruApi.build_login_url(
        settings.DNEVNIK_CLIENT_ID,
        ["EducationalInfo", "CommonInfo", "FriendsAndRelatives"],
        str(URL(settings.URL).joinpath("login/authSchoolAdmin")),
        state=str(message.from_user.id)
    )

    await message.answer(
        **Text(
            "Еще раз приветствуем от Активиум!\n",
            CustomEmoji("⚠️", custom_emoji_id="5447644880824181073"), " Прочитайте внимательно",
            CustomEmoji("👇", custom_emoji_id="5470177992950946662"), "\n\n",

            ExpandableBlockQuote(
                "После прохождения процедуры авторизации от образовательной организации (далее — ОО) Вам и другим "
                "контактам, кого Вы добавите в список администраторов, будет доступен расширенный функционал: "
                "изменение расписания звонков, добавление внеурочных занятий в расписание, публикация новостей и "
                "мероприятий, а также просмотр статистики\n\n"

                "Для прохождения этой процедуры необходимо войти в профиль Дневника.ру с правами администратора ОО. "
                "Если Вы не имеете доступа к такому профилю, попросите администрацию ОО пройти авторизацию, "
                "а потом добавить Вас\n\n"

                "Если у администрации ОО нет возможности зайти в Telegram, то скопируйте ссылку по кнопке и поделитесь "
                "ею любым доступным образом. После прохождения авторизации Вам будет доступен весь функционал "
                "от лица администрации\n\n"

                "Если один из администраторов ОО уже добавлен в Активиум, то Вы можете просто попросить добавить "
                "Вас в список для совместной работы с Активиум"
            )
        ).as_kwargs(),
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Войти в Дневник.ру", icon_custom_emoji_id="5409334318004738910", url=login_url)],
                [InlineKeyboardButton(text="Попросить другого", icon_custom_emoji_id="5465562509425514761", url=share_url)],
                [InlineKeyboardButton(text="Скопировать ссылку", copy_text=CopyTextButton(text=login_url))],
                [InlineKeyboardButton(text="Назад", icon_custom_emoji_id="5467864676320681402", callback_data="start")]
            ]
        )
    )
