from enum import Enum, StrEnum

from aiogram.utils.formatting import Text, CustomEmoji


__all__ = ['EmojiIdList', 'EmojiList']


def emoji(standard: str, custom_emoji_id: str) -> Text:
    """Эмодзи с пробелом после"""

    return Text(CustomEmoji(standard, custom_emoji_id=custom_emoji_id), " ")


class EmojiIdList(StrEnum):
    rocket = "5445284980978621387"
    brick = "5260293700088511294"
    activium = "5406575351272872039"
    android = "5197404349399054325"
    github = "4961044117187462239"
    settings = "5341715473882955310"
    bell = "5458603043203327669"
    histogram = "5231200819986047254"
    school = "5265002646397285605"
    microphone = "5382013970905309819"
    verified = "5440712623219822019"
    hello = "5343984088493599366"
    star = "5435957248314579621"
    outline_star = "5994495149336434048"
    check_mark = "5206607081334906820"
    warning_red = "5420323339723881652"
    dnevnikru = "5409334318004738910"
    share = "5465562509425514761"
    warning_yello = "5447644880824181073"
    backhand_index_pointing_down = "5470177992950946662"
    loading = "5235997383627658618"
    cross = "5210952531676504517"
    plus = "5397916757333654639"
    back = "5467864676320681402"
    pie_chart = "5445255358589182162"
    left = "5877536313623711363"
    update = "5030872266716480568"
    right = "5875506366050734240"
    eyes = "5210956306952758910"
    pencil = "5395444784611480792"
    big_right = "5416117059207572332"
    question = "5452069934089641166"


class EmojiList(Enum):
    rocket = emoji("🚀", EmojiIdList.rocket)
    brick = emoji("⛔️", EmojiIdList.brick)
    activium = emoji("🤓", EmojiIdList.activium)
    settings = emoji("⚙️", EmojiIdList.settings)
    hello = emoji("👋", EmojiIdList.hello)
    star = emoji("⭐️", EmojiIdList.star)
    outline_star = emoji("⭐️", EmojiIdList.outline_star)
    warning_yello = emoji("⚠️", EmojiIdList.warning_yello)
    backhand_index_pointing_down = emoji("👇", EmojiIdList.backhand_index_pointing_down)
    loading = emoji("🔵", EmojiIdList.loading)
    verified = emoji("✅", EmojiIdList.verified)
    histogram = emoji("📊", EmojiIdList.histogram)
    microphone = emoji("🎙", EmojiIdList.microphone)
    bell = emoji("🔔", EmojiIdList.bell)
    school = emoji("🏫", EmojiIdList.school)
    question = emoji("❓", EmojiIdList.question)
    pencil = emoji("✏️", EmojiIdList.pencil)
