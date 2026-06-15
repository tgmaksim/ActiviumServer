from typing import Literal
from datetime import datetime, timedelta, date

from dnevnikru import AioDnevnikruApi

from .types import (
    CumulativeUsersType,
    DailyRegistrationType,
    DailyActionsType,
    UniqueUsersDailyType,
    ClassDistributionType
)

from sqlalchemy import select, exists, case, cast, func, Date

from src.repositories.db_queue import AsyncDBQueue
from src.repositories.sqlalchemy_repository import SqlAlchemyRepository

from src.models.base_model import BaseModel

from src.models.child_model import Child
from src.models.parent_model import Parent
from src.models.session_model import Session
from src.models.statistic_model import Statistic
from src.models.school_admin_model import SchoolAdmin


__all__ = ['SchoolStatisticsRepository']


class SchoolStatisticsRepository(SqlAlchemyRepository[BaseModel]):
    """Репозиторий для получения статистики по образовательной организации"""

    def __init__(self, queue: AsyncDBQueue, school_admin: SchoolAdmin, dnr: AioDnevnikruApi, start_period: datetime, now: datetime):
        super().__init__(queue, BaseModel)

        self.school_admin = school_admin
        self.dnr = dnr
        self.start_period = start_period
        self.now = now

    async def get_users_stats(self) -> tuple[list[CumulativeUsersType], list[DailyRegistrationType]]:
        """Сбор данных о регистрации пользователей"""

        len_period = (self.now - self.start_period).days + 1

        cumulative_users: list[CumulativeUsersType] = [
            {
                "date": (self.start_period + timedelta(days=i)).date(),
                "value": 0
            }
            for i in range(len_period)
        ]

        daily_registrations: list[DailyRegistrationType] = [
            {
                "date": (self.start_period + timedelta(days=i)).date(),
                "parents": 0,
                "children": 0
            }
            for i in range(len_period)
        ]

        # Пользователь связан с образовательной организацией
        parent_in_school_subquery = (
            exists(
                select(Session.parent_id)
                .join(Session.active_child)
                .where(Session.parent_id == Parent.parent_id)
                .where(Child.school_id == self.school_admin.dnevnik_admin.school_id)
            )
        )

        # Является ли пользователь ребенком
        is_child_subquery = (
            case(
                (
                    exists()
                    .where(Child.child_id == Parent.parent_id),
                    True
                ),
                else_=False
            )
        )

        # Все пользователи, которые были зарегистрированы после start_period и связаны с образовательной организацией
        # Также возвращается статус пользователя (родитель или ребенок)
        parents_statement = (
            select(
                Parent,
                is_child_subquery.label("is_child")
            )
            .where(Parent.created_at >= self.start_period)
            .where(parent_in_school_subquery)
            .order_by(Parent.created_at.asc())
        )
        parents_result = await self.queue.execute(parents_statement)
        parents_with_status: list[tuple[Parent, bool]] = parents_result.all()

        # Даты регистраций
        registrations = [parent.created_at.date() for parent, _ in parents_with_status]

        # Подсчет количества зарегистрированных пользователей
        index = 0
        for i in range(len_period):
            while index < len(registrations) and registrations[index] == cumulative_users[i]['date']:
                type_registration: Literal["children", "parents"] = 'children' if parents_with_status[index][1] else 'parents'
                daily_registrations[i][type_registration] += 1

                index += 1

            cumulative_users[i]['value'] = index

        return cumulative_users, daily_registrations

    async def get_daily_actions(self) -> tuple[list[DailyActionsType], list[UniqueUsersDailyType]]:
        # Пользователь связан с образовательной организацией
        parent_in_school_subquery = (
            exists(
                select(Session.parent_id)
                .join(Session.active_child)
                .where(Session.parent_id == Parent.parent_id)
                .where(Child.school_id == self.school_admin.dnevnik_admin.school_id)
            )
        )

        # Является ли пользователь ребенком
        is_child_subquery = (
            case(
                (
                    exists()
                    .where(Child.child_id == Parent.parent_id),
                    True
                ),
                else_=False
            )
        )

        # Дата с учетом часового пояса администратора образовательной организации без времени
        local_date_expr = cast(
            Statistic.created_at + func.make_interval(0, 0, 0, 0, 0, 0, self.school_admin.dnevnik_admin.timezone),
            Date
        )

        # Количество действий и уникальных пользователей за дни для детей и родителей отдельно
        statistics_statement = (
            select(
                local_date_expr.label("local_date"),
                is_child_subquery.label("is_child"),
                func.count(Statistic.statistic_id).label("cnt"),
                func.count(func.distinct(Statistic.parent_id)).label("unique_cnt")
            )
            .join(Parent, Statistic.parent_id == Parent.parent_id)
            .where(parent_in_school_subquery)
            .where(Statistic.created_at >= self.start_period)
            .group_by(local_date_expr, is_child_subquery)
        )

        statistics_result = await self.queue.execute(statistics_statement)
        statistics: list[tuple[date, bool, int, int]] = statistics_result.all()

        statistics_by = {
            (statistic_date, is_child): (count, unique_count)
            for statistic_date, is_child, count, unique_count in statistics
        }

        len_period = (self.now - self.start_period).days + 1

        default = (0, 0)

        daily_actions: list[DailyActionsType] = [
            {
                "date": (statistic_date := (self.start_period + timedelta(days=i)).date()),
                "parents": statistics_by.get((statistic_date, False), default)[0],
                "children": statistics_by.get((statistic_date, True), default)[0]
            }
            for i in range(len_period)
        ]

        unique_users_daily: list[UniqueUsersDailyType] = [
            {
                "date": (statistic_date := (self.start_period + timedelta(days=i)).date()),
                "value": (
                    statistics_by.get((statistic_date, False), default)[1]
                    +
                    statistics_by.get((statistic_date, True), default)[1]
                )
            }
            for i in range(len_period)
        ]

        return daily_actions, unique_users_daily

    async def get_all_users(self) -> tuple[int, int]:
        # Является ли пользователь ребенком
        is_child_subquery = (
            case(
                (
                    exists()
                    .where(Child.child_id == Parent.parent_id)
                    .correlate(Parent),
                    True
                ),
                else_=False
            )
        )

        # Общее число пользователей (детей и родителей) от образовательной организации
        all_users_statement = (
            select(
                is_child_subquery.label("is_child"),
                func.count(func.distinct(Parent.parent_id)).label("count")
            )
            .join(Session, Session.parent_id == Parent.parent_id)
            .join(Session.active_child)
            .where(Child.school_id == self.school_admin.dnevnik_admin.school_id)
            .group_by(is_child_subquery)
        )
        all_users_result = await self.queue.execute(all_users_statement)
        all_users: dict[bool, int] = {is_child: count for is_child, count in all_users_result.all()}

        return (
            all_users.get(False, 0),
            all_users.get(True, 0)
        )

    async def get_class_distribution(self) -> list[ClassDistributionType]:
        # Все учебные группы (классы) и число зарегистрированных детей в них
        groups_statement = (
            select(
                Child.group_id,
                func.count(Child.child_id).label("count")
            )
            .where(Child.school_id == self.school_admin.dnevnik_admin.school_id)
            .group_by(Child.group_id)
        )
        groups_result = await self.queue.execute(groups_statement)
        groups: list[tuple[int, int]] = groups_result.all()

        groups_by_id = {group_id: count for group_id, count in groups}

        # Данные об учебных группах (классах)
        full_groups = await self.dnr.get_groups(list(groups_by_id.keys()))
        # TODO: обработать старую сессию

        class_distribution: list[ClassDistributionType] = [
            {
                "class_name": full_group['group']['name'],
                "count": groups_by_id[full_group['group']['id']]
            }
            for full_group in full_groups
        ]

        return class_distribution
