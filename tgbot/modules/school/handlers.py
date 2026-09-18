from yarl import URL

from aiogram import Router, F

from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, CommandStart
from aiogram.utils.formatting import Text, ExpandableBlockQuote
from aiogram.types import Message

from dnevnikru import AioDnevnikruApi

from src.config.project_config import settings

from ...enums.emoji import EmojiList
from ...enums.modules import ModuleList
from ...enums.commands import CommandList

from .buttons import school_links


__all__ = ['router']

router = Router(name=ModuleList.school)


@router.message(Command(CommandList.school))
async def _cmd_school(message: Message, state: FSMContext):
    """Помощь в прохождении авторизации администратора образовательной организации"""

    await state.clear()

    # Ссылка для отправки сообщения другому пользователю
    share_url = (
        f"tg://msg_url?text=Здравствуйте,+пройдите+авторизацию+в+{settings.PROJECT_NAME_RU},"
        f"+чтобы+мы+могли+публиковать+новости+и+мероприятия&url={settings.BOT_URL}?start=school_auth"
    )

    # Ссылка для прохождения авторизации администратора образовательной организации через Дневник.ру
    login_url = AioDnevnikruApi.build_login_url(
        settings.DNEVNIK_CLIENT_ID,
        ["EducationalInfo", "CommonInfo", "FriendsAndRelatives"],
        str(URL(settings.URL_FOR_TG).joinpath("login/authSchoolAdmin")),
        state=str(message.from_user.id)
    )

    text = Text(
        f"Еще раз приветствуем от {settings.PROJECT_NAME_RU}!\n",
        EmojiList.warning_yello.value, " Прочитайте внимательно", EmojiList.backhand_index_pointing_down.value, "\n\n",

        ExpandableBlockQuote(
            "После прохождения процедуры авторизации от образовательной организации (далее — ОО) Вам и другим "
            "контактам, кого Вы добавите в список администраторов, будет доступен расширенный функционал: "
            "изменение расписания звонков, добавление внеурочных занятий в расписание, публикация новостей и "
            "мероприятий, а также просмотр статистики\n\n"

            "Для прохождения этой процедуры необходимо войти в профиль Дневника.ру с правами администратора ОО. "
            "Если Вы не имеете доступа к такому профилю, попросите администрацию ОО пройти авторизацию "
            "в Telegram-боте, а потом добавить Вас в свои администраторы\n\n"

            "Если у администрации ОО нет возможности зайти в Telegram, то скопируйте ссылку по кнопке и поделитесь "
            "ею любым доступным образом. После прохождения авторизации Вам будет доступен весь функционал "
            "от лица администрации\n\n"

            f"Если один из администраторов ОО уже добавлен в {settings.PROJECT_NAME_RU}, "
            "то Вы можете просто попросить добавить Вас в список своих администраторов для совместной работы"
        )
    )

    reply_markup = school_links(login_url, share_url)

    await message.answer(**text.as_kwargs(), reply_markup=reply_markup)


@router.message(CommandStart(deep_link=True, magic=F.args == "school_auth"))
async def _start_with_school_auth(message: Message, state: FSMContext):
    """Открытие бота по ссылке приглашения администратора образовательной организации"""

    await state.clear()

    text = Text(
        "Здравствуйте! ", EmojiList.hello.value, "\n",
        f"Данный бот предназначен для подключения образовательных организаций к сервису {settings.PROJECT_NAME_RU} ",
        EmojiList.activium.value, "\n\n",

        f"Вас пригласили, чтобы авторизоваться в {settings.PROJECT_NAME_RU} от образовательной организации. "
        "После этого Вы сможете добавить своих администраторов и пользоваться расширенным функционалом\n\n",

        f"Для авторизации откройте /{CommandList.school}"
    )

    await message.answer(**text.as_kwargs())
