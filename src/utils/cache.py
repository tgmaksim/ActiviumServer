from datetime import datetime, date

from dnevnikru import AioDnevnikruApi
from src.models import Session, Child
from src.support.repositories.cache_repository import CacheRepository
from src.support.schemas.dnevnik_schemas import WorkType


class CacheService:
    @classmethod
    async def get_work_types(
            cls, cache_repository: CacheRepository, dnr: AioDnevnikruApi,
            session: Session, child: Child,
            work_types_id: set[int]
    ) -> dict[int, WorkType]:
        """
        Получение типов работ по идентификаторам

        :param cache_repository: CacheRepository для получения типов работ из кэша, если записаны
        :param dnr: объект AioDnevnikruApi для взаимодействия с Дневником.ру
        :param session: сессия пользователя
        :param child: ребенок (профиль), для которого требуется получить типы работ
        :param work_types_id: идентификаторы необходимых типов работ на уроке
        :return: типы работ по идентификаторам
        """

        if not work_types_id:
            return {}

        # Получение типов работ из кэша
        work_types_key = [f"workType|{work_type_id}" for work_type_id in work_types_id]
        caches = await cache_repository.get_caches(session.session_id, child.child_id, work_types_key)
        results = {
            int(cache.key.split("|")[1]): WorkType(
                title=cache.value['title'],
                abbr=cache.value['abbr']
            )
            for cache in caches
        }

        # Если из кэша все необходимые типы работ получены
        if work_types_id == results.keys():
            return results

        # Иначе запрос к Дневнику.ру
        work_types = await dnr.get_work_types(child.school_id)

        new_caches = []

        for work_type in work_types:
            new_caches.append((
                f"workType|{work_type['id']}",
                {
                    'title': work_type['title'],
                    'abbr': work_type['abbr']
                }
            ))

            if work_type['id'] in work_types_id:
                results[work_type['id']] = WorkType(
                    title=work_type['title'],
                    abbr=work_type['abbr']
                )

        # Запись в кэш для последующих запросов
        await cache_repository.put_caches(session.session_id, child.child_id, new_caches)

        return results

    @classmethod
    async def get_persons_name(
            cls, cache_repository: CacheRepository, dnr: AioDnevnikruApi,
            session: Session, child: Child,
            persons_id: set[int]
    ) -> dict[int, str]:
        """
        Получение имен одноклассников

        :param cache_repository: CacheRepository для получения имен из кэша
        :param dnr: объект AioDnevnikruApi для взаимодействия с Дневником.ру
        :param session: сессия пользователя
        :param child: ребенок (профиль), для которого требуются имена одноклассников
        :param persons_id: идентификаторы одноклассников
        :return: имена одноклассников по идентификаторам
        """

        if not persons_id:
            return {}

        # Получение имен одноклассников из кэша
        persons_id_key = [f"person|{person_id}" for person_id in persons_id]
        caches = await cache_repository.get_caches(session.session_id, child.child_id, persons_id_key)
        results = {
            int(cache.key.split("|")[1]): cache.value['name']
            for cache in caches
        }

        # Если из кэша все необходимые имена одноклассников получены
        if persons_id == results.keys():
            return results

        # Иначе запрос к Дневнику.ру
        persons = await dnr.get_group_persons(child.group_id)

        new_caches = []

        for person in persons:
            new_caches.append((
                f"person|{person['id']}",
                {
                    'name': person['shortName']
                }
            ))

            if person['id'] in persons_id:
                results[person['id']] = person['shortName']

        # Запись в кэш для последующих запросов
        await cache_repository.put_caches(session.session_id, child.child_id, new_caches)

        return results

    @classmethod
    async def get_periods(
            cls, cache_repository: CacheRepository, dnr: AioDnevnikruApi,
            session: Session, child: Child
    ) -> list[dict]:
        """
        Получение отчетных периодов в текущем году

        :param cache_repository: CacheRepository для получения отчетных периодов из кэша
        :param dnr: объект AioDnevnikruApi для взаимодействия с Дневником.ру
        :param session: сессия пользователя
        :param child: ребенок (профиль), для которого требуются отчетные периоды
        :return: список отчетных периодов
        """

        cache_key = "periods"

        # Получение из кэша
        if cache := await cache_repository.get_cache(session.session_id, child.child_id, cache_key):
            return cache.value
        else:
            # Запрос из Дневника.ру
            periods = await dnr.get_reporting_periods(child.group_id)

            # Сохранение в кэш для последующих запросов
            await cache_repository.put_cache(session.session_id, child.child_id, cache_key, periods)

            return periods

    @classmethod
    async def get_period(
            cls, cache_repository: CacheRepository, dnr: AioDnevnikruApi,
            session: Session, child: Child,
            day: date
    ) -> dict:
        """
        Получение отчетного периода, в который входит день

        :param cache_repository: CacheRepository для получения отчетных периодов из кэша
        :param dnr: объект AioDnevnikruApi для взаимодействия с Дневником.ру
        :param session: сессия пользователя
        :param child: ребенок (профиль), для которого требуется отчетный период
        :param day: дата дня
        :return: отчетный период
        """

        periods = await cls.get_periods(cache_repository, dnr, session, child)
        periods = sorted(periods, key=lambda p: datetime.fromisoformat(p['start']))

        return cls.get_active_period(periods, day)

    @classmethod
    def get_active_period(cls, periods: list[dict], day: date) -> dict:
        """
        Получение отчетного периода, в который входит день

        :param periods: отчетные периоды, отсортированные по возрастанию
        :param day: дата дня
        :return: отчетный период
        """

        active_period = None
        for number, period in enumerate(periods):
            start = datetime.fromisoformat(period['start']).date()

            # Если следующий отчетный период уже после дня, то день входит в прошлый
            if start > day:
                active_period = periods[max(0, number - 1)]  # Если день до первого отчетного периода, то первый
                break

        # Если нет такого отчетного периода, который начинается после дня, то это последний отчетный период
        if active_period is None:
            active_period = periods[-1]

        return active_period

    @classmethod
    async def get_subjects(
            cls, cache_repository: CacheRepository, dnr: AioDnevnikruApi,
            session: Session, child: Child
    ) -> list[dict]:
        """
        Получение предметов в учебной группе

        :param cache_repository: CacheRepository для получения предметов из кэша
        :param dnr: объект AioDnevnikruApi для взаимодействия с Дневником.ру
        :param session: сессия пользователя
        :param child: ребенок (профиль), для которого требуются предметы
        :return: список предметов
        """

        cache_key = "subjects"

        # Получение из кэша
        if cache := await cache_repository.get_cache(session.session_id, child.child_id, cache_key):
            return cache.value
        else:
            # Запрос из Дневника.ру
            subjects = await dnr.get_subjects(child.group_id)

            # Сохранение в кэш для последующих запросов
            await cache_repository.put_cache(session.session_id, child.child_id, cache_key, subjects)

            return subjects
