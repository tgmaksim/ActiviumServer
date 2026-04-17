import traceback
import ai.request

from aiogram import html
from urllib.parse import quote

from typing import Optional
from datetime import timezone, timedelta

from .base_service import BaseService
from ..config.project_config import settings
from ..repositories.log_uow import LogUnitOfWork
from ..repositories.statistic_repository import StatName


ADMIN_TIMEZONE = timezone(timedelta(hours=settings.ADMIN_TIMEZONE))

__all__ = ['LogService']


class LogService(BaseService[LogUnitOfWork]):
    async def log(
            self,
            *,
            ip: Optional[str] = None,
            path: str,
            session_id: Optional[str] = None,
            status: bool = True,
            method: Optional[str] = None,
            value: str,
    ):
        async with self.uow_factory() as uow:
            await uow.log_repository.add_log(ip=ip, path=path, session_id=session_id, status=status, method=method, value=value)

    async def stat(self, parent_id: Optional[int], key: str):
        async with self.uow_factory() as uow:
            await uow.statistics_repository.add_statistic(parent_id, key)

    async def send_stats_notification(self):
        async with self.uow_factory() as uow:
            count_all, max_created_at, min_created_at, count_errors = await uow.notification_repository.get_count()

            logs_open_url = settings.LOGS_PGADMIN_OPEN.format(
                min_created_at=quote(str(min_created_at)), max_created_at=quote(str(max_created_at)))

            from_date = min_created_at.astimezone(ADMIN_TIMEZONE).strftime('%e %b. %H:%M:%S')
            ru_logs = 'лога' if 2 <= count_all % 10 <= 4 else ('лог' if count_all % 10 == 1 else 'логов')

            text = (f"<b>#Статистика Активиум c {from_date}</b>\n\n"
                    f"<b>Логи</b>\nСобрано {count_all} {ru_logs}\n")

            if count_errors:
                text += f"⚠️ Обнаружены ошибки ({count_errors} шт.)\n"
            else:
                text += "Ошибок не обнаружено\n"

            text += f"<a href=\"{html.quote(logs_open_url)}\">Открыть логи</a>\n"

            # await uow.notification_repository.delete_notifications(max_created_at)
            # await uow.log_repository.add_log(path='stats', value='stats')  # Для точной статистики в следующий раз

            since = min_created_at

            text += "\n<b>Мониторинг запросов</b>\n"
            monitorings = await uow.monitoring_repository.get_stats(since)
            for monitoring in sorted(monitorings, key=lambda m: m[3], reverse=True):
                text += (f"<i>{monitoring[0]}</i>: "
                         f"от {round(monitoring[1].total_seconds() * 1000, 1)} мс "
                         f"до {round(monitoring[2].total_seconds() * 1000, 1)} мс, "
                         f"{round(monitoring[3].total_seconds() * 1000, 1)} мс\n")

            text += "\n<b>Статистика пользования</b>\n"
            count_unique_users = await uow.statistics_repository.get_count_unique_users(since)
            text += f"Уникальных пользователей: {count_unique_users}\n"
            group_statistics = await uow.statistics_repository.get_group_statistics(since)
            for statistic in group_statistics:
                text += f"<i>{statistic[0]}</i>: {statistic[1]}\n"

            text += "\n<i>Таким был день в Активиум...</i>"

            messages = await uow.notification_repository.notify(text)

            count_last_messages = 5
            last_messages = list(map(lambda m: m.message, await uow.statistic_message_repository.get_last_messages(count_last_messages)))
            await uow.statistic_message_repository.write_message(messages[0].text)

        ai_chat = [
            ai.request.Message(role='system', content=self.ai_system()),
            ai.request.Message(role='user', content=f"Последние {len(last_messages)} собранных статистик:\n\n" +
                                                    '\n\n'.join(last_messages) + "Текущий день:\n" + messages[0].text)]

        try:
            ai_message = await ai.request.request(ai_chat)
        except Exception as e:
            ai_message = '\n'.join(traceback.format_exception(e))
        ai_message = f"Обзор ИИ\n{ai_message}"

        for i in range(0, len(ai_message), 4096):
            await uow.notification_repository.notify(ai_message[i:i+4096])

    @staticmethod
    def ai_system():
        return "Во входных данных дана собранная статистика примерно за сутки работы сервера школьного приложения Активиум. Также доступны данные статистики за прошлые дни, чтобы можно было сравнить и получить динамику. Для каждого дня собирается мониторинг скорости запросов. На каждый запрос дается минимальное, максимальное и медианное значение скорости ответа. Нужно сравнить каждое значение с прошлыми результатами, и только если есть расхождения по каждому отдельно запросу (в любую сторону), то сообщить об этом, иначе сказать, что все стабильно. Далее идет статистика: количество уникальных пользователей, которые совершили хотя бы одно действие, и количество произведенных действий. Для каждого действия дается короткое описание. Нужно на основе всех данных, а также опираясь на прошлые данные, написать сводку по статистике и мониторингу ТОЛЬКО по СЕГОДНЯШНЕМУ (последнему) дню, не нужно анализировать прошлые дни отдельно, только использовать для анализа сегодняшнего. В тексте должно быть больше слов, чем переписанных цифр, например вместо приведения количества запросов на каждый запрос, можно написать, что сегодня бело замечено увеличение таких-то запросов, или сегодня активность приложения была низкая, или сегодня зарегистрировалось <несколько> человек. При этом не делай своих выводов и предположений, почему такой-то параметр изменился, только факты. Особое внимание обращай на количество регистраций (если есть) и активных пользователей. Если ты приводишь названия запросов, то префиксы api/ можешь опускать. В сообщениях используй нейтральный стиль, без эмодзи. Пиши понятно и информативно. Не пиши большое введение и заключение своего сообщения."

    @staticmethod
    def ai_header():
        return "Названия статистики:\n" + '\n'.join(map(lambda n: f"{n.name}: {n.value}", StatName._member_map_.values()))
