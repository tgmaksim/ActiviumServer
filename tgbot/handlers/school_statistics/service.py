import calendar
import numpy as np

from typing import TypeVar
from datetime import datetime, date

from src.config.project_config import settings

from .types import (
    DataWithDateType,
    CumulativeUsersType,
    DailyRegistrationType,
    DailyActionsType,
    UniqueUsersDailyType,
    ClassDistributionType
)

from pathlib import Path

from matplotlib import pyplot as plt
from matplotlib import dates as mdates
from matplotlib.ticker import FuncFormatter
from matplotlib.backends.backend_pdf import PdfPages


__all__ = ['create_admin_stats']

Item = TypeVar("Item", bound=DataWithDateType)


def sort_by_date(items: list[Item]) -> list[Item]:
    """Сортировка списка с данными по дате"""

    return sorted(items, key=lambda x: x['date'])


def month_formatter(x, _):
    """Названия месяцев по-русски"""

    months = {
        1: "Январь",
        2: "Февраль",
        3: "Март",
        4: "Апрель",
        5: "Май",
        6: "Июнь",
        7: "Июль",
        8: "Август",
        9: "Сентябрь",
        10: "Октябрь",
        11: "Ноябрь",
        12: "Декабрь"
    }

    dt = mdates.num2date(x)
    return months[dt.month]


def get_month_centers(dates: list[date]) -> list[datetime]:
    months = set()
    centers = []

    for dt in sorted(dates):
        key = (dt.year, dt.month)
        if key in months:
            continue

        months.add(key)

        days_in_month = calendar.monthrange(dt.year, dt.month)[1]
        center_day = days_in_month // 2

        centers.append(datetime(dt.year, dt.month, center_day))

    return centers


def plot_cumulative_users(ax: plt.Axes, cumulative_users: list[CumulativeUsersType]):
    """
    Добавление линейного графика с количеством зарегистрированных пользователей.
    Даты указаны только для точек, где значение увеличилось по сравнению с предыдущим днем

    :param ax: объект подграфика
    :param cumulative_users: данные с количеством зарегистрированных пользователей на каждый день
    """

    title = "Число зарегистрированных пользователей"
    no_data = "Нет данных"
    ylabel = "Пользователи"
    color = "C0"

    data = sort_by_date(cumulative_users)
    if not data:
        ax.set_title(title)
        ax.text(0.5, 0.5, no_data, ha="center", va="center", transform=ax.transAxes)
        return

    dates = [row['date'] for row in data]
    values = [row['value'] for row in data]

    ax.plot(dates, values, marker="o", markersize=1.8, linewidth=2.0, color=color)
    ax.set_title(title, pad=10)
    ax.set_ylabel(ylabel)
    ax.grid(True, axis="y", alpha=0.25)

    # Отображаются только те даты, по которым наблюдался рост
    prev = values[0]
    for dt, val in zip(dates, values):
        if val > prev:
            label = dt.strftime("%e %b.")
            ax.annotate(
                label,
                (dt, val),
                textcoords="offset points",
                xytext=(0, -18),
                ha="center",
                va="top",
                fontsize=8,
                rotation=0,
            )
        prev = val

    ax.set_xlim(min(dates), max(dates))

    # Основные тики — начало месяца (для линий сетки)
    ax.xaxis.set_major_locator(mdates.MonthLocator())

    # Дополнительные тики — центр месяца (для подписей)
    month_centers = get_month_centers(dates)
    ax.set_xticks(month_centers, minor=True)

    # Подписи основных тиков не нужны
    ax.xaxis.set_major_formatter(plt.NullFormatter())

    # Дополнительные тики
    ax.xaxis.set_minor_formatter(FuncFormatter(month_formatter))

    # Подписи только для дополнительных тиков
    ax.tick_params(axis="x", which="major", length=5)
    ax.tick_params(axis="x", which="minor", length=0, pad=10)


def plot_daily_registrations_stacked(ax: plt.Axes, daily_registrations: list[DailyRegistrationType]):
    """
    Добавление столбчатой диаграммы с количеством регистраций за каждый день.
    Отображаются только те дни, когда произошла хотя бы одна регистрация

    :param ax: объект подграфика
    :param daily_registrations: данные с количеством регистраций родителей и детей за каждый день
    """

    title = "Регистрации пользователей по дням"
    no_data = "Нет данных"
    ylabel = "Регистрация"
    parents_label = "Родители"
    children_label = "Дети"
    parent_color = "C1"
    child_color = "C2"

    data = sort_by_date(daily_registrations)

    if not data:
        ax.set_title(title)
        ax.text(0.5, 0.5, no_data, ha="center", va="center", transform=ax.transAxes)

    dates = [row['date'] for row in data]
    parents = np.array([row['parents'] for row in data], dtype=int)
    children = np.array([row['children'] for row in data], dtype=int)

    width = 0.8
    ax.bar(dates, parents, width=width, color=parent_color, label=parents_label)
    ax.bar(dates, children, width=width, bottom=parents, color=child_color, label=children_label)

    ax.set_title(title, pad=10)
    ax.set_ylabel(ylabel)
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(frameon=False, ncol=2, loc="upper left")

    ax.set_xlim(min(dates), max(dates))

    # Основные тики — начало месяца (для линий сетки)
    ax.xaxis.set_major_locator(mdates.MonthLocator())

    # Дополнительные тики — центр месяца (для подписей)
    month_centers = get_month_centers(dates)
    ax.set_xticks(month_centers, minor=True)

    # Подписи основных тиков не нужны
    ax.xaxis.set_major_formatter(plt.NullFormatter())

    # Дополнительные тики
    ax.xaxis.set_minor_formatter(FuncFormatter(month_formatter))

    # Подписи только для дополнительных тиков
    ax.tick_params(axis="x", which="major", length=5)
    ax.tick_params(axis="x", which="minor", length=0, pad=10)


def plot_registration_pie(ax: plt.Axes, parents_total: int, children_total: int):
    """
    Добавление круговой диаграммы, показывающей общее количество зарегистрированных пользователей
    с разбивкой по число родителей и детей

    :param ax: объект подграфика
    :param parents_total: число зарегистрированных родителей
    :param children_total: число зарегистрированных детей
    """

    title = "Общее число пользователей на данный момент"
    no_data = "Нет данных"
    labels = ["Родители", "Дети"]
    parent_color = "C1"
    child_color = "C2"

    total = parents_total + children_total
    if total <= 0:
        ax.set_title(title)
        ax.text(0.5, 0.5, no_data, ha="center", va="center", transform=ax.transAxes)
        return

    values = [parents_total, children_total]
    colors = [parent_color, child_color]

    def _autopct(pct: float) -> str:
        absolute = int(round(pct * total / 100.0))
        return f"{pct:.1f}%\n({absolute})"

    ax.pie(
        values,
        labels=labels,
        colors=colors,
        autopct=_autopct,
        startangle=90,
        textprops={"fontsize": 9},
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
    )
    ax.set_title(title, pad=10)
    ax.axis("equal")


def plot_daily_actions_stacked(ax: plt.Axes, daily_actions: list[DailyActionsType]):
    """
    Добавление столбчатой диаграммы, отображающей общее количество действий в день,
    с распределением между родителями и детьми. На оси X указаны месяцы

    :param ax: объект подграфика
    :param daily_actions: данные с количеством действия родителей и детей за каждый день
    """

    title = "Общее количество совершенных действий (активность) в приложении"
    no_data = "Нет данных"
    ylabel = "Действия"
    parents_label = "Родители"
    children_label = "Дети"
    parent_color = "C1"
    child_color = "C2"

    data = sort_by_date(daily_actions)
    if not data:
        ax.set_title(title)
        ax.text(0.5, 0.5, no_data, ha="center", va="center", transform=ax.transAxes)
        return

    dates = [row['date'] for row in data]
    parents = np.array([row['parents'] for row in data], dtype=int)
    children = np.array([row['children'] for row in data], dtype=int)

    ax.bar(dates, parents, width=0.8, color=parent_color, label=parents_label)
    ax.bar(dates, children, width=0.8, bottom=parents, color=child_color, label=children_label)

    ax.set_title(title, pad=10)
    ax.set_ylabel(ylabel)
    ax.grid(True, axis="y", alpha=0.25)
    ax.legend(frameon=False, ncol=2, loc="upper left")

    ax.set_xlim(min(dates), max(dates))

    # Основные тики — начало месяца (для линий сетки)
    ax.xaxis.set_major_locator(mdates.MonthLocator())

    # Дополнительные тики — центр месяца (для подписей)
    month_centers = get_month_centers(dates)
    ax.set_xticks(month_centers, minor=True)

    # Подписи основных тиков не нужны
    ax.xaxis.set_major_formatter(plt.NullFormatter())

    # Дополнительные тики
    ax.xaxis.set_minor_formatter(FuncFormatter(month_formatter))

    # Подписи только для дополнительных тиков
    ax.tick_params(axis="x", which="major", length=5)
    ax.tick_params(axis="x", which="minor", length=0, pad=10)


def plot_unique_users_daily(ax: plt.Axes, unique_users_daily: list[UniqueUsersDailyType]):
    """
    Добавление линейного графика с количеством уникальных активных пользователей за каждый день

    :param ax: объект подграфика
    :param unique_users_daily: данные с количеством уникальных пользователей за каждый день
    """

    title = "Число уникальных пользователей каждый день"
    no_data = "Нет данных"
    ylabel = "Пользователи"
    color = "C3"

    data = sort_by_date(unique_users_daily)
    if not data:
        ax.set_title(title)
        ax.text(0.5, 0.5, no_data, ha="center", va="center", transform=ax.transAxes)
        return

    dates = [row['date'] for row in data]
    values = [row['value'] for row in data]

    ax.plot(dates, values, marker="o", markersize=1.8, linewidth=2.0, color=color)
    ax.set_title(title, pad=10)
    ax.set_ylabel(ylabel)
    ax.grid(True, axis="y", alpha=0.25)

    ax.set_xlim(min(dates), max(dates))

    # Основные тики — начало месяца (для линий сетки)
    ax.xaxis.set_major_locator(mdates.MonthLocator())

    # Дополнительные тики — центр месяца (для подписей)
    month_centers = get_month_centers(dates)
    ax.set_xticks(month_centers, minor=True)

    # Подписи основных тиков не нужны
    ax.xaxis.set_major_formatter(plt.NullFormatter())

    # Дополнительные тики
    ax.xaxis.set_minor_formatter(FuncFormatter(month_formatter))

    # Подписи только для дополнительных тиков
    ax.tick_params(axis="x", which="major", length=5)
    ax.tick_params(axis="x", which="minor", length=0, pad=10)


def plot_class_distribution(ax: plt.Axes, class_distribution: list[ClassDistributionType]):
    """
    Добавление столбчатой диаграммы с распределением детей по классам

    :param ax: объект подграфика
    :param class_distribution: данные с количеством детей в каждом классе
    """

    title = "Распределение детей по классам"
    ylabel = "Число детей"

    classes = [x['class_name'] for x in class_distribution]
    counts = [x['count'] for x in class_distribution]

    ax.bar(classes, counts, color="C2")

    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.grid(True, axis="y", alpha=0.25)


def create_admin_stats(
    output_path: Path,
    cumulative_users: list[CumulativeUsersType],
    all_users: tuple[int, int],
    daily_registrations: list[DailyRegistrationType],
    daily_actions: list[DailyActionsType],
    unique_users_daily: list[UniqueUsersDailyType],
    class_distribution: list[ClassDistributionType]
):
    """
    Создание отчета с диаграммами и графиками по зарегистрированным и активным пользователям и их действиям.
    В результате получается лист PDF

    :param output_path: путь к файлу для сохранения статистики в формате PDF
    :param cumulative_users: данные с количеством зарегистрированных пользователей на каждый день
    :param all_users: количество зарегистрированных родителей и детей
    :param daily_registrations: данные с количеством регистраций родителей и детей за каждый день
    :param daily_actions: данные с количеством действия родителей и детей за каждый день
    :param unique_users_daily: данные с количеством уникальных пользователей за каждый день
    :param class_distribution: данные с количеством детей в каждом классе
    """

    figsize = (18, 24)
    dpi = 300
    style = "seaborn-v0_8-whitegrid"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with plt.style.context(style):
        fig = plt.figure(figsize=figsize, dpi=dpi, constrained_layout=True)
        gs = fig.add_gridspec(5, 2, height_ratios=[1.15, 1.0, 1.05, 1.0, 1.0])

        ax1 = fig.add_subplot(gs[0, :])
        ax2 = fig.add_subplot(gs[1, :])
        ax3 = fig.add_subplot(gs[2, :])
        ax4 = fig.add_subplot(gs[3, :])
        ax5 = fig.add_subplot(gs[4, 0])
        ax6 = fig.add_subplot(gs[4, 1])

        # Верхняя строка: график общего количества зарегистрированных пользователей
        plot_cumulative_users(ax1, cumulative_users)

        # Вторая строка: столбчатая диаграмма с данными о ежедневных регистрациях
        plot_daily_registrations_stacked(ax2, daily_registrations)

        # Третья строка: столбчатая диаграмма совершенных действия за каждый день
        plot_daily_actions_stacked(ax3, daily_actions)

        # Четвертая строка: график уникальных пользователей за каждый день
        plot_unique_users_daily(ax4, unique_users_daily)

        # Пятая строка: круговая диаграмма с числом зарегистрированных родителей и детей
        # и круговая диаграмма с распределением детей по классам
        plot_registration_pie(ax5, *all_users)
        plot_class_distribution(ax6, class_distribution)

        title = f"Статистика использования {settings.PROJECT_NAME_RU} пользователями от образовательной организации"
        fig.suptitle(title, fontsize=18, fontweight="bold")

        with PdfPages(output_path) as pdf:
            pdf.savefig(fig, dpi=dpi, bbox_inches="tight")

        plt.close(fig)
